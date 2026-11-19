with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('ส่งออก')
if pos != -1:
    print("Snippet around ส่งออก:")
    print(text[pos-200:pos+800])

pos2 = text.find('fileIn')
if pos2 != -1:
    print("Snippet around fileIn:")
    print(text[pos2-200:pos2+800])
