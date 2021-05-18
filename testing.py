from PIL import Image, ImageDraw

if __name__ == "__main__":
    im1 = Image.new("RGB", (1000, 1000), "red")
    random_draw = ImageDraw.Draw(im1)
    random_draw.ellipse((230, 120, 280, 170), fill=0)
    im2 = Image.new("RGB", (1000, 1000), "white")
    mask = Image.new("L", im1.size, 0)
    draw = ImageDraw.Draw(mask)
    draw.pieslice((140, 50, 260, 170), 30, 90, fill=255)
    im = Image.composite(im1, im2, mask)
    for pixel in im.getdata():
        if pixel == (0, 0, 0):
            print("Border")
            break
