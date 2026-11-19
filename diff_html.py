with open(r'c:\Users\Windows10\Downloads\SMG Hub.html', 'r', encoding='utf-8', errors='ignore') as f:
    user_text = f.read()

with open(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\index.html', 'r', encoding='utf-8') as f:
    hub_text = f.read()

print("User HTML length:", len(user_text))
print("Hub HTML length:", len(hub_text))

# Let's check if there are differences in script or sampleData or anything
pos_u = user_text.find('function sampleData')
pos_h = hub_text.find('function sampleData')
print("pos_u:", pos_u, "pos_h:", pos_h)
if pos_u != -1:
    print("User sampleData:", user_text[pos_u:pos_u+300])
