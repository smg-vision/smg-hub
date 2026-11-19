with open(r'c:\Users\Windows10\Downloads\SMG Hub.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = text.find('function renderHead')
print(text[pos:pos+1200])
