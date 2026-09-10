# Args :
# - Path to the pdf file
# - Page number

import sys
args = sys.argv
if len(args) != 3:
    print("Invalid Argument Count : ", len(args))
    sys.exit()

import fitz
from PIL import Image
import io
import platform
import subprocess
import shutil

def copy_image_to_clipboard(image):
    """
    Copies a PIL Image to the system clipboard so it can be pasted (Ctrl+V)
    into other applications. Works on Windows, macOS, and Linux.
    """
    system = platform.system()

    if image.mode != "RGB":
        image = image.convert("RGB")

    if system == "Windows":
        _copy_windows(image)
    elif system == "Darwin":
        _copy_macos(image)
    elif system == "Linux":
        _copy_linux(image)
    else:
        raise NotImplementedError(f"Clipboard copy not supported on {system}")


def _copy_windows(image):
    import win32clipboard

    output = io.BytesIO()
    image.save(output, "BMP")
    data = output.getvalue()[14:]  # strip BMP file header for CF_DIB
    output.close()

    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
    win32clipboard.CloseClipboard()


def _copy_macos(image):
    # macOS clipboard wants PNG via NSPasteboard; osascript + a temp file
    # is the simplest dependency-free route.
    import tempfile
    import os

    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        image.save(f, "PNG")
        temp_path = f.name

    script = f'''
    set the clipboard to (read (POSIX file "{temp_path}") as «class PNGf»)
    '''
    subprocess.run(["osascript", "-e", script], check=True)
    os.remove(temp_path)


def _copy_linux(image):
    # Requires xclip (X11) or wl-copy (Wayland) to be installed.
    output = io.BytesIO()
    image.save(output, "PNG")
    png_data = output.getvalue()
    output.close()

    if shutil.which("wl-copy"):  # Wayland
        subprocess.run(["wl-copy", "--type", "image/png"], input=png_data, check=True)
    elif shutil.which("xclip"):  # X11
        subprocess.run(
            ["xclip", "-selection", "clipboard", "-t", "image/png"],
            input=png_data,
            check=True,
        )
    else:
        raise RuntimeError(
            "No clipboard tool found. Install 'xclip' (X11) or 'wl-clipboard' (Wayland)."
        )

 
# Get pdf page
doc = fitz.open(args[1])
page = doc[int(args[2])-1]
pix = page.get_pixmap(dpi=200)
# Get PIL image
mode = "RGBA" if pix.alpha else "RGB"
img  = Image.frombytes(mode, (pix.width, pix.height), pix.samples)
# Copy image to clipboard
copy_image_to_clipboard(img)