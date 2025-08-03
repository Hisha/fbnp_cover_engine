import pangocairocffi
import cairocffi as cairo
import pangocffi as pango
from PIL import Image

def render_text(text, font_family, font_size, color, box_size, align):
    if not font_family or not font_size:
        raise ValueError("Font family and font size must be specified explicitly.")

    width, height = box_size

    # ✅ Create a transparent surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)
    context.set_source_rgba(0, 0, 0, 0)  # Transparent background
    context.paint()

    # ✅ Create Pango layout
    layout = pangocairocffi.create_layout(context)
    layout.set_width(width * pango.SCALE)
    layout.set_height(height * pango.SCALE)
    layout.set_wrap(pango.WrapMode.WORD_CHAR)

    # ✅ Apply font settings
    font_desc = pango.FontDescription(f"{font_family} {font_size}")
    layout.set_font_description(font_desc)
    layout.set_text(text)

    # ✅ Alignment
    align_map = {
        "center": pango.Alignment.CENTER,
        "right": pango.Alignment.RIGHT,
        "left": pango.Alignment.LEFT
    }
    layout.set_alignment(align_map.get(align.lower(), pango.Alignment.LEFT))

    # ✅ Draw text
    context.set_source_rgb(color[0]/255, color[1]/255, color[2]/255)
    pangocairocffi.show_layout(context, layout)

    # ✅ Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)

    return img

def render_rotated_text(text, font_family, font_size, color, box_size, angle):
    img = render_text(text, font_family, font_size, color, box_size, align="center")
    return img.rotate(angle, expand=True)
