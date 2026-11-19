with open(r'c:\Users\Windows10\Downloads\SMG Hub.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'editToggle|editbar|CAN_EDIT', text)]
for pos in matches[:5]:
    print(text[pos-50:pos+200])
    print('='*50)
