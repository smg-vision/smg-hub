from PIL import Image

img_path = r'C:/Users/Windows10/.gemini/antigravity/brain/094cc230-8eeb-4577-bd8c-54c0573428ed/.user_uploaded/media_1794909723154_5e29757c.jpg'
im = Image.open(img_path)
print("Image size:", im.size)
