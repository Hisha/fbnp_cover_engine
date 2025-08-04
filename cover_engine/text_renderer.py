import os
import subprocess
import requests
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image

FONTS_DIR = os.path.expanduser("~/.fbnp_cover_engine/fonts")
os.makedirs(FONTS_DIR, exist_ok=True)


def verify_or_download_font(font_family):
    """
    Check if font is installed system-wide; if not, download from Google Fonts.
    Refresh font cache after download.
    """
    # Check system font availability first
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if result.stdout.strip():
            print(f"✅ Font '{font_family}' is available.")
            return font_family
    except FileNotFoundError:
        print("⚠️ fc-list not available, skipping system font check.")

    # Try Google Fonts download
    print(f"🔍 Font '{font_family}' not found. Attempting Google Fonts download...")
    folder_name = font_family.lower().replace(" ", "")
    file_name = font_family.replace(" ", "") + "-Regular.ttf"  # Example: Lobster → Lobster-Regular.ttf
    font_url = f"https://github.com/google/fonts/raw/main/ofl/{folder_name}/{file_name}"
    font_path = os.path.join(FONTS_DIR, file_name)

    try:
        r = requests.get(font_url, timeout=15)
        if r.status_code == 200:
            with open(font_path, "wb") as f:
                f.write(r.content)
            print(f"✅ Downloaded font '{font_family}' to {font_path}")
            # Refresh font cache
            subprocess.run(["fc-cache", "-f", FONTS_DIR])
            return font_family
        else:
            print(f"⚠️ Failed to download font '{font_family}' (status {r.status_code}). Using default.")
    except Exception as e:
        print(f"⚠️ Font download error: {e}. Using default font.")

    return "DejaVu Serif"  # Safe fallback


def render_text(text, font_family, font_size, color, box_size, align="left", valign="top"):
    """
    Render text into a transparent image using Pango + Cairo.
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Set up Pango layout
    layout = PangoCairo.create_layout(context)
    layout.set_text(text, -1)

    # Font & size
    font_desc = Pango.FontDescription()
    font_desc.set_family(font_family)
    font_desc.set_size(font_size * Pango.SCALE)
    layout.set_font_description(font_desc)

    # Horizontal alignment
    if align == "center":
        layout.set_alignment(Pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(Pango.Alignment.RIGHT)
    else:
        layout.set_alignment(Pango.Alignment.LEFT)

    # Calculate text size
    ink_rect, logical_rect = layout.get_extents()
    text_width = logical_rect.width // Pango.SCALE
    text_height = logical_rect.height // Pango.SCALE

    # Vertical alignment offset
    if valign == "middle":
        y_offset = (height - text_height) // 2
    elif valign == "bottom":
        y_offset = height - text_height
    else:
        y_offset = 0

    # Apply color
    context.set_source_rgba(color[0] / 255, color[1] / 255, color[2] / 255, 1)

    # Move context for alignment
    context.move_to(0, y_offset)
    PangoCairo.show_layout(context, layout)

    # Convert to PIL
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img


def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size, align="center", valign="middle")
    return img.rotate(angle, expand=True)
