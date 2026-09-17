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
    from gradio.networking import setup_tunnel, GRADIO_API_SERVER
    from gradio.tunneling import BINARY_PATH, Tunnel
    import httpx, subprocess, re
    import urllib.request
    for _ in range(60):
        try:
            urllib.request.urlopen('http://127.0.0.1:7898/api/health', timeout=2)
            break
        except Exception:
            time.sleep(1)
    proxy = os.environ.get('HTTPS_PROXY')
    if proxy:
        info = httpx.get(GRADIO_API_SERVER, timeout=30).json()[0]
        cert = runtime / 'share-ca.crt'
        cert.write_text(info['root_ca'])
        config = runtime / 'share.ini'
        config.write_text('[common]\nserver_addr = '+info['host']+'\nserver_port = '+str(info['port'])+'\nhttp_proxy = '+proxy+'\ntls_enable = true\ntls_trusted_ca_file = '+str(cert)+'\nlog_level = info\n\n['+secrets.token_hex(16)+']\ntype = http\nlocal_ip = 127.0.0.1\nlocal_port = 7898\nsubdomain = random\nuse_encryption = true\nuse_compression = true\n')
        tunnel = Tunnel(info['host'], int(info['port']), '127.0.0.1', 7898, secrets.token_hex(16), str(cert))
        tunnel.download_binary()
        proc = subprocess.Popen([BINARY_PATH, '-c', str(config)], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        url = None
        for line in proc.stdout:
            print(line.strip(), flush=True)
            match = re.search(r'https://[a-zA-Z0-9.-]+\.gradio\.live', line)
            if match:
                url = match.group(0)
                break
        if not url:
            raise RuntimeError('Public tunnel failed')
    else:
        url = setup_tunnel('127.0.0.1', 7898, secrets.token_urlsafe(32), None, None)
    (runtime / 'public.json').write_text(json.dumps({'url': url, 'created': time.time(), 'note': 'Gradio share tunnel; temporary, expires after one week.'}))
    print('PUBLIC_URL=' + url, flush=True)

if os.environ.get('STUDY_SHARE') == '1':
    threading.Thread(target=share, daemon=True).start()
uvicorn.run('server:app', host='127.0.0.1', port=int(os.environ.get('PORT', 7898)), access_log=False)
