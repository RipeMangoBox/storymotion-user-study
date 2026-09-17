"""Standalone paired-video questionnaire. Responses never enter the public repo."""
import hashlib, json, os, random, secrets, sqlite3, time
from pathlib import Path
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

ROOT = Path(__file__).resolve().parent
DATA = Path(os.environ.get('STUDY_DATA', ROOT / 'runtime'))
DATA.mkdir(parents=True, exist_ok=True)
CATALOG = json.loads((DATA / 'catalog.json').read_text())
SAMPLES = {s['id'] + ':' + s['mode']: s for s in CATALOG['samples']}
MEDIA = {v['media_id']: str(DATA / 'blind_media' / (v['media_id'] + '.mp4')) for s in SAMPLES.values() for v in s['methods'].values()}
CAMERA = ['camera_text', 'camera_geometry', 'framing']
HUMAN = ['human_text', 'human_physics']
DB = DATA / 'responses.sqlite3'
def connect():
    c = sqlite3.connect(DB, timeout=20)
    c.row_factory = sqlite3.Row
    return c
with connect() as c:
    c.execute('PRAGMA journal_mode=WAL')
    c.executescript('''CREATE TABLE IF NOT EXISTS sessions (
        id INTEGER PRIMARY KEY, token TEXT UNIQUE NOT NULL, created REAL NOT NULL,
        language TEXT NOT NULL, is_test INTEGER NOT NULL, plan TEXT NOT NULL,
        submitted REAL, receipt TEXT);
        CREATE TABLE IF NOT EXISTS answers (
        session_id INTEGER NOT NULL, idx INTEGER NOT NULL, ratings TEXT NOT NULL,
        watched TEXT NOT NULL, elapsed REAL NOT NULL, saved REAL NOT NULL,
        PRIMARY KEY(session_id,idx));''')

app = FastAPI(docs_url=None, redoc_url=None, openapi_url=None)
app.add_middleware(CORSMiddleware, allow_origins=['https://ripemangobox.github.io'], allow_methods=['GET', 'POST', 'PUT'], allow_headers=['Authorization', 'Content-Type'])

@app.middleware('http')
async def headers(request, call_next):
    response = await call_next(request)
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['Referrer-Policy'] = 'no-referrer'
    if request.url.path.startswith('/api/'):
        response.headers['Cache-Control'] = 'no-store'
    return response

def auth(request):
    token = request.headers.get('Authorization', '').removeprefix('Bearer ')
    if len(token) != 64:
        raise HTTPException(401, 'Session not found. Please resume using the same browser.')
    with connect() as c:
        row = c.execute('SELECT * FROM sessions WHERE token=?', (hashlib.sha256(token.encode()).hexdigest(),)).fetchone()
    if row is None:
        raise HTTPException(401, 'Session not found')
    return row

def public_session(row):
    trials = []
    for i, p in enumerate(json.loads(row['plan'])):
        s = SAMPLES[p['key']]
        trials.append({'index': i, 'mode': s['mode'], 'human_text': s['human_text'], 'camera_text': s['camera_text'], 'duration': s['duration'], 'videos': ['/media/' + s['methods'][m]['media_id'] for m in p['methods']], 'questions': CAMERA if s['mode'] == 'given' else HUMAN + CAMERA})
    with connect() as c:
        answers = {str(r['idx']): {'ratings': json.loads(r['ratings']), 'watched': json.loads(r['watched']), 'elapsed': r['elapsed']} for r in c.execute('SELECT * FROM answers WHERE session_id=?', (row['id'],))}
    return {'version': CATALOG['version'], 'trials': trials, 'answers': answers, 'submitted': row['submitted'] is not None, 'receipt': row['receipt'], 'is_test': bool(row['is_test'])}

class Start(BaseModel):
    language: str = Field(pattern='^(en|zh)$')
    consent: bool
    test_key: str = ''

@app.get('/api/health')
def health():
    return {'ok': True, 'version': CATALOG['version'], 'given': 20, 'joint': 20}

@app.post('/api/start')
def start(payload: Start):
    if not payload.consent:
        raise HTTPException(400, 'Consent required')
    is_test = bool(payload.test_key and secrets.compare_digest(payload.test_key, os.environ.get('STUDY_TEST_KEY', secrets.token_hex(32))))
    if payload.test_key and not is_test:
        raise HTTPException(403, 'Invalid test key')
    token = secrets.token_hex(32)
    rng = random.Random(secrets.randbits(128))
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        n = c.execute('SELECT COUNT(*) FROM sessions WHERE is_test=?', (int(is_test),)).fetchone()[0]
        plan = []
        for mode in ['given', 'joint']:
            samples = [s for s in CATALOG['samples'] if s['mode'] == mode]
            sides = [False] * 10 + [True] * 10
            rng.shuffle(sides)
            block = []
            for i, s in enumerate(samples):
                baselines = sorted(m for m in s['methods'] if m != 'mainline')
                baseline = baselines[(i + n) % len(baselines)]
                methods = [baseline, 'mainline'] if sides[i] else ['mainline', baseline]
                block.append({'key': s['id'] + ':' + mode, 'methods': methods})
            rng.shuffle(block)
            plan.extend(block)
        cursor = c.execute('INSERT INTO sessions(token,created,language,is_test,plan) VALUES(?,?,?,?,?)', (hashlib.sha256(token.encode()).hexdigest(), time.time(), payload.language, int(is_test), json.dumps(plan)))
        row = c.execute('SELECT * FROM sessions WHERE id=?', (cursor.lastrowid,)).fetchone()
    return {'token': token, **public_session(row)}

@app.get('/api/session')
def session(request: Request):
    return public_session(auth(request))

class Answer(BaseModel):
    ratings: dict[str, str]
    watched: list[bool] = Field(min_length=2, max_length=2)
    elapsed: float = Field(ge=0, le=604800)

@app.put('/api/answers/{index}')
def answer(index: int, payload: Answer, request: Request):
    row = auth(request)
    if row['submitted'] is not None:
        raise HTTPException(409, 'Already submitted')
    if not 0 <= index < 40:
        raise HTTPException(400, 'Invalid trial')
    plan = json.loads(row['plan'])
    s = SAMPLES[plan[index]['key']]
    expected = CAMERA if s['mode'] == 'given' else HUMAN + CAMERA
    if set(payload.ratings) != set(expected) or not all(v in ['-2', '-1', '0', '1', '2', 'na'] for v in payload.ratings.values()):
        raise HTTPException(400, 'Please answer every criterion')
    if not all(payload.watched):
        raise HTTPException(400, 'Watch both videos before continuing')
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        if c.execute('SELECT submitted FROM sessions WHERE id=?', (row['id'],)).fetchone()[0] is not None:
            raise HTTPException(409, 'Already submitted')
        previous = c.execute('SELECT COUNT(*) FROM answers WHERE session_id=? AND idx<?', (row['id'], index)).fetchone()[0]
        if previous != index:
            raise HTTPException(400, 'Complete preceding trials first')
        c.execute('INSERT INTO answers VALUES(?,?,?,?,?,?) ON CONFLICT(session_id,idx) DO UPDATE SET ratings=excluded.ratings,watched=excluded.watched,elapsed=excluded.elapsed,saved=excluded.saved', (row['id'], index, json.dumps(payload.ratings), json.dumps(payload.watched), payload.elapsed, time.time()))
    return {'saved': True, 'index': index}

@app.post('/api/submit')
def submit(request: Request):
    row = auth(request)
    with connect() as c:
        c.execute('BEGIN IMMEDIATE')
        current = c.execute('SELECT submitted,receipt FROM sessions WHERE id=?', (row['id'],)).fetchone()
        if current['submitted'] is not None:
            return {'submitted': True, 'receipt': current['receipt']}
        if c.execute('SELECT COUNT(*) FROM answers WHERE session_id=?', (row['id'],)).fetchone()[0] != 40:
            raise HTTPException(400, 'All 40 trials are required')
        receipt = secrets.token_hex(6).upper()
        c.execute('UPDATE sessions SET submitted=?, receipt=? WHERE id=?', (time.time(), receipt, row['id']))
    return {'submitted': True, 'receipt': receipt}

@app.get('/media/{media_id}')
def media(media_id: str):
    path = MEDIA.get(media_id)
    if path is None:
        raise HTTPException(404)
    return FileResponse(path, media_type='video/mp4', headers={'Cache-Control': 'public,max-age=86400'})

@app.get('/')
def index():
    return FileResponse(ROOT / 'web/index.html', headers={'Cache-Control': 'no-cache'})

@app.get('/{asset}')
def asset(asset: str):
    if asset not in ['app.js', 'style.css', 'config.js']:
        raise HTTPException(404)
    return FileResponse(ROOT / 'web' / asset, headers={'Cache-Control': 'no-cache'})
