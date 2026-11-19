with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
pos_start = text.find('// Pre-populate with initial data')
pos_end = text.find('window.claude = {', pos_start)
print("Initial data block length:", pos_end - pos_start)
print(text[pos_start:pos_start+300])
print("...")
print(text[pos_end-300:pos_end])
