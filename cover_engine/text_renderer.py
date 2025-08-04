import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image

def render_text(text, font_family, font_size, color, box_size, align="left"):
    """
    Render text using Pango + Cairo into a PIL image.
    """
    width, height = box_size

    # Create Cairo surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Create Pango layout
    layout = PangoCairo.create_layout(context)
    font_desc = Pango.FontDescription(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text, -1)

    # Alignment
    if align == "center":
        layout.set_alignment(Pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(Pango.Alignment.RIGHT)
    else:
        layout.set_alignment(Pango.Alignment.LEFT)

    # Set color
    context.set_source_rgb(color[0] / 255, color[1] / 255, color[2] / 255)

    # Render text
    PangoCairo.update_layout(context, layout)
    context.move_to(0, 0)
    PangoCairo.show_layout(context, layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
