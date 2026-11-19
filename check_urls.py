with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
scripts = re.findall(r'<script[^>]*src=["\']([^"\']+)["\']', text)
print("External scripts in original_frame:", scripts)

assets_proxy = re.findall(r'https://[^\s"\'<>]+', text)
print("Unique domains/URLs:", set([u.split('/')[2] for u in assets_proxy if '/' in u]))
for u in set(assets_proxy):
    if 'anthropic' in u or 'claude' in u:
        print("Claude URL:", u[:120])
