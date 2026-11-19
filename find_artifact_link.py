with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = [m.start() for m in re.finditer(r'85duaSYVxZYbf5cGzDU96W', text)]
for pos in matches:
    print(text[pos-100:pos+300])
    print('='*50)
