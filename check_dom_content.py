path = r'c:\Users\Windows10\Downloads\SMG Hub.html'
with open(path, 'r', encoding='utf-8', errors='ignore') as f:
    text = f.read()

import re

# Remove script tags and style tags
no_scripts = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL)
no_styles = re.sub(r'<style[^>]*>.*?</style>', '', no_scripts, flags=re.DOTALL)

# Find all visible text or elements
print("Length without scripts & styles:", len(no_styles))

# Check for cards or list items or product names
items = re.findall(r'<div[^>]*class=["\'][^"\']*card[^"\']*["\'][^>]*>(.*?)</div>', no_styles, re.DOTALL)
print("Cards found:", len(items))

# Let's search for Thai text in the HTML body
thai_texts = re.findall(r'[\u0E00-\u0E7F]+(?:\s+[\u0E00-\u0E7F0-9/.-]+)*', no_styles)
print("Total Thai text segments in DOM:", len(thai_texts))
unique_thai = list(dict.fromkeys([t.strip() for t in thai_texts if len(t.strip()) > 5]))
print(f"Unique Thai phrases ({len(unique_thai)}):")
for t in unique_thai[:30]:
    print(" -", t)
