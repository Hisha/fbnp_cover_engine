import pangocffi as pango
import cairocffi as cairo
from PIL import Image

def render_text(text, font_path, font_size, color, box_size, align="center"):
    """
    Render text into a box using Pango+Cairo.
    Returns a PIL.Image object with transparent background.
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Setup Pango layout
    layout = pango.create_layout(context)
    layout.set_text(text)
    desc = pango.FontDescription()
    desc.set_family("Sans")  # or extract from font_path if needed
    desc.set_absolute_size(font_size * pango.SCALE)
    layout.set_font_description(desc)

    # Dynamic sizing: shrink if doesn't fit
    while True:
        ink_rect, logical_rect = layout.get_pixel_extents()
        if logical_rect.width <= width and logical_rect.height <= height:
            break
        font_size -= 2
        desc.set_absolute_size(font_size * pango.SCALE)
        layout.set_font_description(desc)
        if font_size < 10:
            break

    # Alignment
    if align == "center":
        context.move_to((width - logical_rect.width) / 2, (height - logical_rect.height) / 2)
    elif align == "left":
        context.move_to(0, (height - logical_rect.height) / 2)
    elif align == "right":
        context.move_to(width - logical_rect.width, (height - logical_rect.height) / 2)

    # Set text color
    r, g, b = [c / 255.0 for c in color]
    context.set_source_rgb(r, g, b)

    # Draw text
    context.show_layout(layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), bytes(buf), "raw", "BGRA", 0, 1)
    img = img.convert("RGBA")
    return img


def render_rotated_text(text, font_path, font_size, color, box_size, angle=90):
    """
    Render rotated text (e.g., spine text).
    Returns PIL.Image rotated and ready to paste.
    """
    img = render_text(text, font_path, font_size, color, box_size, align="center")
    return img.rotate(angle, expand=True)
