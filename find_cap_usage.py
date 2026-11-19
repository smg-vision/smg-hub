with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'capabilities', text)]
for pos in matches:
    print(text[pos-50:pos+200])
    print('='*50)
