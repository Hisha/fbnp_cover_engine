import pangocairocffi
import cairocffi as cairo
import pangocffi as pango
from PIL import Image
import io

def render_text(text, font_path, font_size=64, color=(0, 0, 0), box_size=(800, 200), align="center"):
    width, height = box_size

    # Create Cairo surface and context
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Create Pango layout
    layout = pangocairocffi.create_layout(context)
    font_desc = pango.FontDescription(f"{font_path} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text)

    # Alignment
    if align == "center":
        layout.set_alignment(pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(pango.Alignment.RIGHT)
    else:
        layout.set_alignment(pango.Alignment.LEFT)

    # Draw text
    context.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
    pangocairocffi.show_layout(context, layout)

    # Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)

    return img


def render_rotated_text(text, font_path, font_size=64, color=(0, 0, 0), box_size=(800, 200), angle=90):
    img = render_text(text, font_path, font_size, color, box_size)
    return img.rotate(angle, expand=True)
