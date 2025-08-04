import os
import requests
import pangocairocffi
import cairocffi as cairo
from pangocffi import FontDescription
from PIL import Image
import io
import subprocess

FONTS_DIR = os.path.expanduser("~/.fbnp_cover_engine/fonts")
os.makedirs(FONTS_DIR, exist_ok=True)


def resolve_font(font_family):
    """
    Ensure the requested font is available locally or system-wide.
    If not, download from Google Fonts.
    """
    normalized = font_family.lower().replace(" ", "")
    font_path = os.path.join(FONTS_DIR, f"{normalized}.ttf")

    # Check if already downloaded
    if os.path.exists(font_path):
        return font_family

    # Check if available system-wide
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Font '{font_family}' found on system.")
            return font_family
    except FileNotFoundError:
        pass

    # Attempt to download from Google Fonts
    print(f"🔍 Font '{font_family}' not found locally. Downloading from Google Fonts...")
    try:
        url = f"https://github.com/google/fonts/raw/main/ofl/{normalized}/{normalized}-regular.ttf"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Font downloaded and saved to {font_path}")
            return font_family
        else:
            raise Exception(f"Font download failed (status {r.status_code})")
    except Exception as e:
        print(f"⚠️ Failed to download font '{font_family}': {e}")
        print("➡️ Falling back to default font: Arial")
        return "Arial"


def render_text(text, font_family, font_size, color, box_size, align="left"):
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    layout = pangocairocffi.create_layout(context)

    # ✅ Create font description properly
    font_desc = FontDescription.from_string(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)

    layout.set_text(text)

    # ✅ Alignment
    if align == "center":
        layout.set_alignment(pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(pango.Alignment.RIGHT)
    else:
        layout.set_alignment(pango.Alignment.LEFT)

    # ✅ Color
    context.set_source_rgb(color[0] / 255, color[1] / 255, color[2] / 255)
    pangocairocffi.show_layout(context, layout)

    # ✅ Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
