with open(r'c:\Users\Windows10\Downloads\SMG Hub.html', 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

pos = text.find('id="btnExport"')
print("Snippet around btnExport:")
print(text[pos-300:pos+500])
