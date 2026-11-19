with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'data-pdf', text)]
for pos in matches:
    print(text[pos-40:pos+300])
    print('='*50)
