import json, os, secrets, threading, time
from pathlib import Path
import uvicorn

runtime = Path(__file__).resolve().parent / 'runtime'
runtime.mkdir(exist_ok=True)
key = runtime / 'test.key'
if not key.exists():
    key.write_text(secrets.token_hex(32))
    key.chmod(0o600)
os.environ['STUDY_TEST_KEY'] = key.read_text().strip()

def share():
    from gradio.networking import setup_tunnel
    import urllib.request
    for _ in range(60):
        try:
            urllib.request.urlopen('http://127.0.0.1:7898/api/health', timeout=2)
            break
        except Exception:
            time.sleep(1)
    url = setup_tunnel('127.0.0.1', 7898, secrets.token_urlsafe(32), None, None)
    (runtime / 'public.json').write_text(json.dumps({'url': url, 'created': time.time(), 'note': 'Gradio share tunnel; temporary, expires after one week.'}))
    print('PUBLIC_URL=' + url, flush=True)

if os.environ.get('STUDY_SHARE') == '1':
    threading.Thread(target=share, daemon=True).start()
uvicorn.run('server:app', host='127.0.0.1', port=int(os.environ.get('PORT', 7898)), access_log=False)
