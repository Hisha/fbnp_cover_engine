import cairocffi as cairo
import pangocffi as pango
import pangocairocffi
from PIL import Image
import subprocess


def verify_font_available(font_family: str):
    """Check if the font exists on the system using fc-list."""
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if font_family.lower() in result.stdout.lower():
            return True
        else:
            raise ValueError(f"❌ Font '{font_family}' not found on system. Install it and run `fc-cache -fv`.")
    except FileNotFoundError:
        raise RuntimeError("`fc-list` command not found. Please install fontconfig.")


def render_text(text, font_family, font_size, color, box_size, align="left"):
    """Render text using Pango + Cairo into a PIL Image."""
    verify_font_available(font_family)

    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Pango layout
    layout = pangocairocffi.create_layout(context)
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

    # Color
    context.set_source_rgb(color[0] / 255, color[1] / 255, color[2] / 255)
    pangocairocffi.show_layout(context, layout)

    # Convert Cairo surface to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img


def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size)
    return img.rotate(angle, expand=True)
