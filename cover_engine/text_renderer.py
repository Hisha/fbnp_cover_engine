import os
import subprocess
import requests
import pangocairocffi
import cairocffi as cairo
import pangocffi as pango
from PIL import Image

FONTS_DIR = os.path.expanduser("~/.fbnp_cover_engine/fonts")
os.makedirs(FONTS_DIR, exist_ok=True)

def resolve_font(font_family):
    """
    Ensure font is available to Pango.
    If not installed system-wide, download from Google Fonts and refresh font cache.
    Returns the font family name for Pango usage.
    """
    # Check if font is already installed
    if is_font_available(font_family):
        print(f"✅ Font '{font_family}' found on system.")
        return font_family

    # Normalize for Google Fonts URL
    normalized = font_family.lower().replace(" ", "")
    font_url = f"https://github.com/google/fonts/raw/main/ofl/{normalized}/{normalized}-regular.ttf"
    font_path = os.path.join(FONTS_DIR, f"{normalized}.ttf")

    try:
        print(f"🔍 Downloading font '{font_family}' from Google Fonts...")
        r = requests.get(font_url, timeout=15)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Font saved at {font_path}")

            # Update font cache
            subprocess.run(["fc-cache", "-f", FONTS_DIR], check=True)
            if is_font_available(font_family):
                print(f"✅ Font '{font_family}' registered successfully.")
                return font_family
        raise Exception("Font download or registration failed.")
    except Exception as e:
        print(f"⚠️ Could not get '{font_family}': {e}. Falling back to 'DejaVu Serif'.")
        return "DejaVu Serif"

def is_font_available(font_name):
    """Check if a font is available in the system font cache."""
    try:
        result = subprocess.run(["fc-list", font_name], capture_output=True, text=True)
        return bool(result.stdout.strip())
    except FileNotFoundError:
        return False

def render_text(text, font_family, font_size, color, box_size, align="left"):
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    layout = pangocairocffi.create_layout(context)
    font_desc = pango.FontDescription.from_string(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text)

    # Alignment
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
