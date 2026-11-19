with open('db_runtime.js', 'r', encoding='utf-8') as f:
    text = f.read()

import re
print("Length of db_runtime.js:", len(text))
print("First 1000 chars:")
print(text[:1000])

# Check fetch, websocket, postMessage, URLs
urls = re.findall(r'https?://[^\s"\'`]+', text)
print("URLs in db_runtime:", urls)

endpoints = re.findall(r'/[_a-zA-Z0-9/.-]+', text)
print("Endpoints sample:", [e for e in endpoints if len(e) > 3][:20])
