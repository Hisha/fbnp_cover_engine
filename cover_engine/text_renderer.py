import os
import requests
import pangocairocffi
import cairocffi as cairo
import pangocffi as pango
from PIL import Image
import subprocess

# Directory to store downloaded fonts
FONTS_DIR = os.path.expanduser("~/.fbnp_cover_engine/fonts")
os.makedirs(FONTS_DIR, exist_ok=True)


def resolve_font(font_family: str) -> str:
    """
    Ensure the requested font is available. If not found system-wide, try to download from Google Fonts.
    Returns the **font family name** (never the path), because Pango needs a family name.
    """
    # Check if font exists system-wide using fc-list
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Font '{font_family}' found on system.")
            return font_family
    except FileNotFoundError:
        print("⚠️ fc-list not available, skipping system font check.")

    # If not found, try downloading from Google Fonts
    print(f"🔍 Font '{font_family}' not found locally. Attempting download from Google Fonts...")
    normalized = font_family.lower().replace(" ", "")
    font_path = os.path.join(FONTS_DIR, f"{normalized}-regular.ttf")

    if not os.path.exists(font_path):
        try:
            url = f"https://github.com/google/fonts/raw/main/ofl/{normalized}/{normalized}-regular.ttf"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                with open(font_path, "wb") as f:
                    f.write(r.content)
                print(f"✅ Font downloaded and saved to {font_path}")
            else:
                raise Exception(f"Download failed with status {r.status_code}")
        except Exception as e:
            print(f"⚠️ Failed to download font '{font_family}': {e}")
            print("➡️ Falling back to default font: DejaVu Sans")
            return "DejaVu Sans"  # Safe fallback

    # Even if downloaded, Pango cannot load by path directly; return original family name
    return font_family


def render_text(text, font_family, font_size, color, box_size, align="left"):
    """
    Render text into a PIL image using Pango for professional layout.
    font_family: Font family name (e.g., 'Arial', 'DejaVu Serif')
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    layout = pangocairocffi.create_layout(context)

    # Ensure font_family is clean
    if "/" in font_family:
        font_family = os.path.splitext(os.path.basename(font_family))[0]

    # Create font description
    font_desc = pango.FontDescription(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text)

    # Alignment
    if align == "center":
        layout.set_alignment(pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(pango.Alignment.RIGHT)
    else:
        layout.set_alignment(pango.Alignment.LEFT)

    # Set color and draw
    context.set_source_rgb(color[0] / 255, color[1] / 255, color[2] / 255)
    pangocairocffi.show_layout(context, layout)

    # Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img


def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
