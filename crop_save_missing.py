from PIL import Image
import os

img_path = r'C:/Users/Windows10/.gemini/antigravity/brain/094cc230-8eeb-4577-bd8c-54c0573428ed/.user_uploaded/media_1794909723154_5e29757c.jpg'
im = Image.open(img_path)

images_dir = r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\images'

# Card 1 (x: 295, y: 177, x2: 423, y2: 300)
c1 = im.crop((295, 178, 423, 298))
# save as 3229dd086c62de477d89f3cdc5c9d795
c1_path = os.path.join(images_dir, '3229dd086c62de477d89f3cdc5c9d795')
c1.save(c1_path, 'JPEG', quality=95)
print("Saved 3229dd086c62de477d89f3cdc5c9d795:", c1.size)

# Card 2 (x: 440, y: 177, x2: 568, y2: 300)
c2 = im.crop((440, 178, 568, 298))
# save as b2e5a53007a58ac587e55bc1bc2a8f9b
c2_path = os.path.join(images_dir, 'b2e5a53007a58ac587e55bc1bc2a8f9b')
c2.save(c2_path, 'JPEG', quality=95)
print("Saved b2e5a53007a58ac587e55bc1bc2a8f9b:", c2.size)
