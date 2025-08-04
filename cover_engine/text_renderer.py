import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")

from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image
import subprocess

def verify_font_available(font_family: str) -> bool:
    """Check if a font family exists on the system using fc-list."""
    try:
        result = subprocess.run(["fc-list", ":family"], capture_output=True, text=True)
        return font_family.lower() in result.stdout.lower()
    except FileNotFoundError:
        print("⚠️ fc-list not found. Skipping font check.")
        return True  # Assume available if we can't check

def render_text(text, font_family, font_size, color, box_size, align="left"):
    """
    Render text using PyGObject Pango + Cairo.
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Create layout
    layout = PangoCairo.create_layout(context)
    font_desc = Pango.FontDescription(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text, -1)

    # Alignment
    alignment = {
        "center": Pango.Alignment.CENTER,
        "right": Pango.Alignment.RIGHT
    }.get(align, Pango.Alignment.LEFT)
    layout.set_alignment(alignment)

    # Word wrap
    layout.set_width(width * Pango.SCALE)
    layout.set_wrap(Pango.WrapMode.WORD)

    # Color
    r, g, b = [c / 255.0 for c in color]
    context.set_source_rgb(r, g, b)

    # Render text
    PangoCairo.update_layout(context, layout)
    PangoCairo.show_layout(context, layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
