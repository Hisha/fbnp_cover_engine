import os
import requests
import pangocairocffi
import cairocffi as cairo
import pangocffi as pango
from pangocffi import FontDescription
from PIL import Image

FONTS_DIR = os.path.expanduser("~/.fbnp_cover_engine/fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

def resolve_font(font_family):
    """
    Ensure the requested font is available locally.
    If not, attempt to download from Google Fonts and return its path.
    """
    normalized = font_family.lower().replace(" ", "")
    font_path = os.path.join(FONTS_DIR, f"{normalized}.ttf")

    if os.path.exists(font_path):
        return font_family

    try:
        import subprocess
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if result.stdout.strip():
            return font_family
    except FileNotFoundError:
        pass

    print(f"🔍 Font '{font_family}' not found locally. Downloading from Google Fonts...")
    try:
        url = f"https://github.com/google/fonts/raw/main/ofl/{normalized}/{normalized}-regular.ttf"
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Font downloaded and saved to {font_path}")
            return font_family
    except Exception as e:
        print(f"⚠️ Failed to download font '{font_family}': {e}")
        print("➡️ Falling back to default font: Arial")
        return "Arial"

def render_text(text, font_family, font_size, color, box_size, align="left"):
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    layout = pangocairocffi.create_layout(context)

    # ✅ Build font description using safe API
    font_desc = FontDescription()
    font_desc.set_family(font_family)
    font_desc.set_size(int(font_size * pango.SCALE))  # convert points to Pango units
    layout.set_font_description(font_desc)
    layout.set_text(text)

    if align == "center":
        layout.set_alignment(pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(pango.Alignment.RIGHT)
    else:
        layout.set_alignment(pango.Alignment.LEFT)

    context.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
    pangocairocffi.show_layout(context, layout)

    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
