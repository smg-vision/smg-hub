with open('db_runtime.js', 'r', encoding='utf-8') as f:
    text = f.read()

# Let's search for install or default export
pos = text.find('install')
print("Install snippet:")
print(text[pos-100:pos+500])
