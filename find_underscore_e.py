with open('original_frame.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos = text.find('_e=')
if pos == -1:
    pos = text.find('const _e')
if pos == -1:
    pos = text.find('let _e')
if pos == -1:
    pos = text.find('function _e')
print(text[pos-50:pos+300])
