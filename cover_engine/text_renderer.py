import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
from PIL import Image
import cairo
import io

def render_text(text, font_family, font_size, color, box_size, align="left", valign="middle"):
    """
    Render text into an image inside a constrained box with proper alignment and wrapping.
    """
    width, height = box_size

    # Create Cairo surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Create Pango layout
    layout = PangoCairo.create_layout(context)
    layout.set_text(text, -1)

    # Font
    font_desc = Pango.FontDescription()
    font_desc.set_family(font_family)
    font_desc.set_size(font_size * Pango.SCALE)
    layout.set_font_description(font_desc)

    # Alignment
    if align == "center":
        layout.set_alignment(Pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(Pango.Alignment.RIGHT)
    else:
        layout.set_alignment(Pango.Alignment.LEFT)

    # Wrap mode and width constraint
    layout.set_width(width * Pango.SCALE)
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)

    # Get text size
    ink_rect, logical_rect = layout.get_extents()
    text_width = logical_rect.width // Pango.SCALE
    text_height = logical_rect.height // Pango.SCALE

    # Horizontal offset
    if align == "center":
        x_offset = (width - text_width) / 2
    elif align == "right":
        x_offset = max(width - text_width, 0)
    else:
        x_offset = 0

    # Vertical alignment
    if valign == "middle":
        y_offset = max((height - text_height) / 2, 0)
    elif valign == "bottom":
        y_offset = max(height - text_height, 0)
    else:  # top
        y_offset = 0

    # Move context to offset
    context.translate(x_offset, y_offset)

    # Set color
    r, g, b = [c / 255.0 for c in color]
    context.set_source_rgb(r, g, b)

    # Render
    PangoCairo.show_layout(context, layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), bytes(buf), "raw", "BGRA", 0, 1)
    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    """
    Render text rotated (used for spine).
    """
    img = render_text(text, font_family, font_size, color, box_size, align="center", valign="middle")
    return img.rotate(angle, expand=True)
