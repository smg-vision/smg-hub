with open('db_runtime.js', 'r', encoding='utf-8') as f:
    text = f.read()

pos = text.find('function $e')
if pos == -1:
    pos = text.find('$e=')
print(text[pos-50:pos+800])
