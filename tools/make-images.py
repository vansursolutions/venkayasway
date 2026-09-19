"""Generates app icons and placeholder gallery images. Run: npm run icons
Replace the generated files in www/icons and www/images with real photos when ready."""
from PIL import Image, ImageDraw
import os

ROOT = os.path.join(os.path.dirname(__file__), '..', 'www')
MAROON = (122, 31, 31); SAFFRON = (217, 116, 28); GOLD = (201, 162, 39); CREAM = (251, 245, 234)

def diya(size, bg, pad_ratio=0.0):
    img = Image.new('RGBA', (size, size), bg)
    d = ImageDraw.Draw(img)
    pad = int(size * pad_ratio)
    s = size - 2 * pad
    cx = size / 2
    # lamp bowl
    d.ellipse([pad + s*0.18, pad + s*0.60, pad + s*0.82, pad + s*0.80], fill=SAFFRON)
    d.ellipse([pad + s*0.24, pad + s*0.58, pad + s*0.76, pad + s*0.66], fill=(240, 160, 70))
    # flame
    d.polygon([(cx, pad + s*0.22), (cx + s*0.11, pad + s*0.48), (cx, pad + s*0.60), (cx - s*0.11, pad + s*0.48)], fill=GOLD)
    d.polygon([(cx, pad + s*0.34), (cx + s*0.05, pad + s*0.48), (cx, pad + s*0.57), (cx - s*0.05, pad + s*0.48)], fill=(255, 235, 170))
    return img

os.makedirs(os.path.join(ROOT, 'icons'), exist_ok=True)
os.makedirs(os.path.join(ROOT, 'images'), exist_ok=True)

for sz in (192, 512):
    diya(sz, MAROON).convert('RGB').save(os.path.join(ROOT, 'icons', f'icon-{sz}.png'))
diya(512, MAROON, 0.12).convert('RGB').save(os.path.join(ROOT, 'icons', 'icon-512-maskable.png'))
diya(180, MAROON).convert('RGB').save(os.path.join(ROOT, 'icons', 'apple-touch-icon.png'))
diya(32, MAROON).save(os.path.join(ROOT, 'icons', 'favicon.png'))

# Gallery placeholders (swamy.jpg / swamy-full.jpg are real photos now; not regenerated)

for i in range(1, 7):
    img = Image.new('RGB', (800, 600), CREAM)
    d = ImageDraw.Draw(img)
    for y in range(600):
        t = y / 600
        d.line([(0, y), (800, y)], fill=(int(251 - 40*t), int(245 - 110*t), int(234 - 190*t)))
    d.text((20, 560), f'Photo {i} - replace images/photo-{i}.jpg', fill=(255, 255, 255))
    img.save(os.path.join(ROOT, 'images', f'photo-{i}.jpg'), quality=85)
print('images generated')
