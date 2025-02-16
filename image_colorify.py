import argparse
import os
from PIL import Image, ImageColor
import toml

parser = argparse.ArgumentParser(
    prog="image_colorify",
    description="colorizes image using input palette",
)

parser.add_argument('filepath')
parser.add_argument('-p', '--palette')
parser.add_argument('-w', '--weight')

args = parser.parse_args()

palette_slug = os.path.split(args.palette)[1].split('.')[0]
palette = []
with open(args.palette) as f:
    obj = toml.loads(f.read())
    for key in obj['colors']:
        for hex in obj['colors'][key]:
            rgb = ImageColor.getcolor(hex, "RGB")
            palette.append(rgb)
    f.close()

im = Image.open(args.filepath)
wt = max(0, min(float(args.weight), 1))

def sq_dist(p1, p2):
    return sum([
        (p1[0]-p2[0])**2, (p1[1]-p2[1])**2, (p1[2]-p2[2])**2,
    ])

def weighted_avg(p1, p2, wt):
    r1, g1, b1 = p1
    r2, g2, b2 = p2
    r = max(0, min(int((1-wt)*r1 + wt*r2), 255))
    g = max(0, min(int((1-wt)*g1 + wt*g2), 255))
    b = max(0, min(int((1-wt)*b1 + wt*b2), 255))
    return r, g, b

px = im.load()
memo = {}

for i in range(im.size[0]):
    for j in range(im.size[1]):
        pixel_color = px[i, j]
        closest_color = []
        closest_dist = 1000000000
        if pixel_color in memo:
            closest_color = memo[pixel_color]
        else:
            for palette_color in palette:
                d = sq_dist(pixel_color, palette_color)
                if d<closest_dist:
                    closest_dist = d
                    closest_color = palette_color
            memo[pixel_color] = closest_color
        px[i, j] = weighted_avg(pixel_color, closest_color, wt)

head, tail = os.path.split(args.filepath)
tail = f'{palette_slug}-{tail}'
im.save(os.path.join(head, tail))
