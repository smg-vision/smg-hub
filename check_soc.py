with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('const SOC =')
print(text[pos:pos+400])
