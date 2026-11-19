from PIL import Image

img_path = r'C:/Users/Windows10/.gemini/antigravity/brain/094cc230-8eeb-4577-bd8c-54c0573428ed/.user_uploaded/media_1794909723154_5e29757c.jpg'
im = Image.open(img_path)

# Card 1 image
c1_img = im.crop((293, 175, 425, 305))
c1_img.save(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\c1_crop.png')

# Card 2 image
c2_img = im.crop((438, 175, 570, 305))
c2_img.save(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\c2_crop.png')

print("Saved c1_crop.png and c2_crop.png")
