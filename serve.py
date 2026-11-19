import http.server
import socket
import os
import sys
import json
import hashlib
import time
import threading
import social_sync

DIRECTORY = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(DIRECTORY, 'data.json')
IMAGES_DIR = os.path.join(DIRECTORY, 'images')

def detect_mime(filepath):
    try:
        with open(filepath, 'rb') as fp:
            head = fp.read(32)
            if head.startswith(b'\xff\xd8\xff'):
                return 'image/jpeg'
            elif head.startswith(b'\x89PNG\r\n\x1a\n'):
                return 'image/png'
            elif head.startswith(b'RIFF') and b'WEBP' in head:
                return 'image/webp'
            elif head.startswith(b'%PDF'):
                return 'application/pdf'
            elif head.startswith(b'GIF8'):
                return 'image/gif'
    except Exception:
        pass
    return None

class Handler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def guess_type(self, path):
        norm = os.path.normpath(path)
        if os.path.isfile(norm):
            mime = detect_mime(norm)
            if mime:
                return mime
        return super().guess_type(path)

    def end_headers(self):
        self.send_header('Cache-Control', 'no-cache, no-store, must-revalidate')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        super().end_headers()

    def do_OPTIONS(self):
        self.send_response(200)
        self.end_headers()

    def send_json(self, data, status=200):
        body = json.dumps(data, ensure_ascii=False).encode('utf-8')
        self.send_response(status)
        self.send_header('Content-Type', 'application/json; charset=utf-8')
        self.send_header('Content-Length', str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_POST(self):
        if self.path == '/api/save':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                data = json.loads(body)
                if isinstance(data, dict) and 'plan' in data and isinstance(data['plan'], list):
                    data['plan'].sort(key=lambda p: (str(p.get('date', '')), str(p.get('id', ''))), reverse=True)
                
                temp_file = DATA_FILE + '.tmp'
                with open(temp_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
                
                if os.path.exists(DATA_FILE):
                    try:
                        os.replace(temp_file, DATA_FILE)
                    except Exception:
                        os.remove(DATA_FILE)
                        os.rename(temp_file, DATA_FILE)
                else:
                    os.rename(temp_file, DATA_FILE)

                self.send_json({'ok': True, 'savedAt': time.strftime('%Y-%m-%d %H:%M:%S')})
                return
            except Exception as e:
                self.send_json({'ok': False, 'error': str(e)}, status=500)
                return

        elif self.path == '/api/upload':
            try:
                content_type = self.headers.get('Content-Type', '')
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length)
                
                if 'application/json' in content_type:
                    payload = json.loads(body.decode('utf-8'))
                    import base64
                    raw_b64 = payload.get('data', '')
                    if ',' in raw_b64:
                        raw_b64 = raw_b64.split(',', 1)[1]
                    raw_bytes = base64.b64decode(raw_b64)
                else:
                    raw_bytes = body

                file_id = hashlib.md5(raw_bytes).hexdigest()
                os.makedirs(IMAGES_DIR, exist_ok=True)
                dest = os.path.join(IMAGES_DIR, file_id)
                with open(dest, 'wb') as f:
                    f.write(raw_bytes)

                self.send_json({'ok': True, 'id': file_id, 'size': len(raw_bytes)})
                return
            except Exception as e:
                self.send_json({'ok': False, 'error': str(e)}, status=500)
                return

        elif self.path == '/api/extract-social':
            try:
                length = int(self.headers.get('Content-Length', 0))
                body = self.rfile.read(length).decode('utf-8')
                payload = json.loads(body)
                url = payload.get('url', '').strip()
                if not url:
                    self.send_json({'ok': False, 'error': 'URL is required'}, status=400)
                    return
                res = social_sync.extract_social_url(url)
                self.send_json(res)
                return
            except Exception as e:
                self.send_json({'ok': False, 'error': str(e)}, status=500)
                return

        elif self.path == '/api/sync-social':
            try:
                length = int(self.headers.get('Content-Length', 0))
                urls = []
                if length > 0:
                    body = self.rfile.read(length).decode('utf-8')
                    if body.strip():
                        payload = json.loads(body)
                        urls = payload.get('urls', [])
                        if isinstance(payload.get('url'), str) and payload['url']:
                            urls.append(payload['url'])
                res = social_sync.sync_smartgreen_page(urls=urls)
                self.send_json(res)
                return
            except Exception as e:
                self.send_json({'ok': False, 'error': str(e)}, status=500)
                return

        self.send_response(404)
        self.end_headers()

class DualStackServer(http.server.ThreadingHTTPServer):
    allow_reuse_address = False
    def server_bind(self):
        try:
            self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        except Exception:
            pass
        super().server_bind()

def background_periodic_sync():
    """Runs periodic sync every 6 hours"""
    time.sleep(30) # wait 30s after boot
    while True:
        try:
            print("[Auto-Sync] Checking Smart Green Facebook & TikTok channels...")
            social_sync.sync_smartgreen_page()
        except Exception as e:
            print("[Auto-Sync] Error:", e)
        time.sleep(6 * 3600)

if __name__ == '__main__':
    port = 8080
    address = ("", port)
    
    # Start background auto-sync thread
    sync_thread = threading.Thread(target=background_periodic_sync, daemon=True)
    sync_thread.start()

    try:
        DualStackServer.address_family = socket.AF_INET6
        httpd = DualStackServer(address, Handler)
        print(f"SMG Hub Server (dual-stack) on port {port} at {DIRECTORY}")
    except Exception as e:
        DualStackServer.address_family = socket.AF_INET
        httpd = DualStackServer(("0.0.0.0", port), Handler)
        print(f"SMG Hub Server (IPv4) on port {port} at {DIRECTORY}")
        
    httpd.serve_forever()
