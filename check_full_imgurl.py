with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('const imgUrl =')
print(text[pos:pos+600])
