# Args :
# - Path to the pdf file
# - Page number
# - Output path

WINDOW_HEIGHT = 1000

import sys
args = sys.argv
if len(args) != 4:
    print("Invalid Argument Count : ", len(args))
    sys.exit()


import fitz
from PIL import Image, ImageTk, ImageDraw
import tkinter as tk

# Get pdf page
doc = fitz.open(args[1])
page = doc[int(args[2])-1]
pix = page.get_pixmap(dpi=200)

# Get it as PIL image
mode = "RGBA" if pix.alpha else "RGB"
img  = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
resized_img = img.resize((int(WINDOW_HEIGHT * pix.width/pix.height), WINDOW_HEIGHT), Image.LANCZOS)

# Tkinter stuff
root = tk.Tk()
canvas = tk.Canvas(root, width=WINDOW_HEIGHT * pix.width/pix.height, height=WINDOW_HEIGHT)
canvas.pack()

tk_img = ImageTk.PhotoImage(resized_img)
canvas.create_image(0, 0, anchor="nw", image=tk_img)


# Selection
points_list = []
line_ids_list = []
def on_press(event):
    global points_list, line_ids_list
    line_ids_list.append([])
    points_list.append([(event.x, event.y)])

def on_drag(event):
    global points_list, line_ids_list
    points_list[-1].append((event.x, event.y))
    if len(points_list[-1]) > 1:
        x0, y0 = points_list[-1][-2]
        x1, y1 = points_list[-1][-1]
        line = canvas.create_line(x0, y0, x1, y1, fill="red", width=2)
        line_ids_list[-1].append(line)

def on_release(event):
    global points_list, line_ids_list
    if len(points_list[-1]) < 3:
        # Remove current selection
        for lid in line_ids_list[-1]:
            canvas.delete(lid)
        line_ids_list.pop()
        points_list.pop()
    else:
        # Close the loop
        x0, y0 = points_list[-1][-1]
        x1, y1 = points_list[-1][0]
        line = canvas.create_line(x0, y0, x1, y1, fill="red", width=2)
        line_ids_list[-1].append(line)

def on_enter(event):
    global points_list, line_ids_list, img
    # Scale all points
    for i in range(len(points_list)):
        for j in range(len(points_list[i])):
            points_list[i][j] = (int(points_list[i][j][0] * (pix.height / WINDOW_HEIGHT)), int(points_list[i][j][1] * (pix.height / WINDOW_HEIGHT)))
    # Build a single mask covering all polygons
    mask = Image.new("L", img.size, 0)
    draw = ImageDraw.Draw(mask)
    for points in points_list:
        draw.polygon(points, fill=255)

    result = Image.new("RGBA", img.size, (255, 255, 255, 255))
    result.paste(img.convert("RGBA"), (0, 0), mask)

    # Crop to the bounding box covering ALL selections combined
    bbox = mask.getbbox()
    if bbox is None:
        raise ValueError("Selections have zero area, nothing to crop")

    cropped = result.crop(bbox)
    cropped.save(args[3])
    root.destroy()

def on_escape(event):
    global points_list, line_ids_list
    if len(points_list) == 0:
        root.destroy()
    else:
        for line_ids in line_ids_list:
            for lid in line_ids:
                canvas.delete(lid)
        points_list = []
        line_ids_list = []

    
canvas.bind("<ButtonPress-1>", on_press)
canvas.bind("<B1-Motion>", on_drag)
canvas.bind("<ButtonRelease-1>", on_release)
root.bind("<Return>", on_enter)
root.bind("<Escape>", on_escape)

root.mainloop()