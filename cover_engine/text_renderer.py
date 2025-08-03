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


def resolve_font(font_family):
    """
    Ensure the requested font is available locally or system-wide.
    If downloaded, refresh font cache and return family name (not path).
    """
    # Check if available system-wide
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if result.stdout.strip():
            return font_family  # Font is installed system-wide
    except FileNotFoundError:
        pass

    # Download from Google Fonts
    normalized = font_family.lower().replace(" ", "")
    font_path = os.path.join(FONTS_DIR, f"{normalized}-regular.ttf")

    if os.path.exists(font_path):
        return font_family  # Already downloaded, just return the family name

    print(f"🔍 Font '{font_family}' not found. Downloading...")
    url = f"https://github.com/google/fonts/raw/main/ofl/{normalized}/{normalized}-regular.ttf"

    try:
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(response.content)

            # Update font cache so Pango can see it
            subprocess.run(["fc-cache", "-f", FONTS_DIR], check=False)
            print(f"✅ Font downloaded and cache updated.")
            return font_family  # Still return the family name
        else:
            raise Exception(f"Download failed: HTTP {response.status_code}")
    except Exception as e:
        print(f"⚠️ Failed to get font '{font_family}': {e}. Falling back to Arial.")
        return "Arial"


def render_text(text, font_path_or_name, font_size, color, box_size, align="left"):
    """
    Render text into an image using Pango with Cairo.
    Supports both local font files and system fonts.
    """
    width, height = box_size

    # Create Cairo surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Create Pango layout
    layout = pangocairocffi.create_layout(context)
    font_desc = pango.FontDescription(f"{font_path_or_name} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text)

    # Alignment
    if align == "center":
        layout.set_alignment(pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(pango.Alignment.RIGHT)
    else:
        layout.set_alignment(pango.Alignment.LEFT)

    # Color
    context.set_source_rgb(color[0] / 255, color[1] / 255, color[2] / 255)
    pangocairocffi.show_layout(context, layout)

    # Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_path_or_name, font_size, color, box_size, angle=90):
    """
    Render rotated text (used for spine).
    """
    img = render_text(text, font_path_or_name, font_size, color, box_size)
    return img.rotate(angle, expand=True)
