with open('index.html', 'r', encoding='utf-8') as f:
    text = f.read()

import re
matches = list(re.finditer(r'formImages', text))
print("formImages occurrences:", len(matches))
for m in matches:
    idx = m.start()
    print("At", idx, ":")
    print(text[max(0, idx-40):min(len(text), idx+100)])
    print("="*40)
