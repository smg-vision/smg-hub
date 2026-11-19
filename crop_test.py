from PIL import Image

img_path = r'C:/Users/Windows10/.gemini/antigravity/brain/094cc230-8eeb-4577-bd8c-54c0573428ed/.user_uploaded/media_1794909723154_5e29757c.jpg'
im = Image.open(img_path)

# In the screenshot:
# Width: 1024, Height: 576
# Card 1 is roughly from x: 290 to 425, y: 325 to 565
# The photo inside card 1 is roughly x: 295 to 420, y: 330 to 490
# Card 2 is roughly from x: 435 to 570, y: 325 to 565
# The photo inside card 2 is roughly x: 440 to 565, y: 330 to 490

# Let's save a test strip to inspect coordinates
test_strip = im.crop((280, 310, 580, 500))
test_strip.save(r'C:\Users\Windows10\.gemini\antigravity\scratch\smg-hub\test_strip.png')
print("Saved test_strip.png")
