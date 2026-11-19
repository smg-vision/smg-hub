with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re

matches = [m.start() for m in re.finditer(r'db\.CCPy_cYa\.js', text)]
for pos in matches:
    print(text[pos-100:pos+200])
    print('='*50)

# Check how capabilities are fetched in Script 1
cap_fetch = re.findall(r'[a-zA-Z0-9_]+\.CCPy_cYa\.js', text)
print("Matches for CCPy_cYa:", cap_fetch)

# Search for the string format used to import or fetch capability files
for m in re.finditer(r'import\(|fetch\(|\.src\s*=', text):
    pos = m.start()
    snippet = text[pos-30:pos+100]
    if any(k in snippet for k in ['cap', 'preamble', '_f', 'manifest', 'chunk']):
        print("Snippet:", snippet)
