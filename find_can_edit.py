with open(r'c:\Users\Windows10\Downloads\SMG Hub.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'CAN_EDIT', text)]
for pos in matches:
    print(text[pos-40:pos+150])
    print('='*50)
