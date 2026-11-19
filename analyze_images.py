import os

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'
files = os.listdir(images_dir)
print(f"Total files in images: {len(files)}")

# Check file sizes
sizes = [os.path.getsize(os.path.join(images_dir, f)) for f in files]
print(f"Min size: {min(sizes)}, Max size: {max(sizes)}, Avg size: {sum(sizes)//len(sizes)}")

# Check file headers to detect mime types (PNG, JPEG, WEBP, PDF, etc.)
types = {}
for f in files:
    with open(os.path.join(images_dir, f), 'rb') as fp:
        head = fp.read(16)
        t = 'unknown'
        if head.startswith(b'\x89PNG\r\n\x1a\n'):
            t = 'png'
        elif head.startswith(b'\xff\xd8\xff'):
            t = 'jpeg'
        elif head.startswith(b'RIFF') and b'WEBP' in head:
            t = 'webp'
        elif head.startswith(b'%PDF'):
            t = 'pdf'
        elif head.startswith(b'GIF8'):
            t = 'gif'
        elif head.startswith(b'{\\rtf'):
            t = 'rtf'
        elif head.startswith(b'{') or head.startswith(b'['):
            t = 'json'
        types[t] = types.get(t, 0) + 1

print("File types detected in images folder:", types)
