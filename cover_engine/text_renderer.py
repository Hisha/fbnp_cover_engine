import subprocess
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image


def verify_font_available(font_family):
    """
    Check if font is installed on the system.
    Raise ValueError if missing.
    """
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if not result.stdout.strip():
            raise ValueError(f"❌ Font '{font_family}' is not installed. Please install it and run again.")
    except FileNotFoundError:
        raise RuntimeError("❌ 'fc-list' command not found. Install fontconfig to check fonts.")


def render_text(text, font_family, font_size, color, box_size, align="left", valign="top"):
    """
    Render text with:
    - Word wrapping
    - Hyphenation for long words
    - Horizontal and vertical alignment
    - Truncates text if it cannot fit after wrapping
    """
    width, height = box_size

    # Create Cairo surface
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # Pango layout
    layout = PangoCairo.create_layout(context)
    layout.set_width(width * Pango.SCALE)  # Enable wrapping
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)  # Wrap on word/character boundaries
    layout.set_text(text, -1)

    # Font
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

    # Calculate layout size
    ink_rect, logical_rect = layout.get_extents()
    text_width = logical_rect.width // Pango.SCALE
    text_height = logical_rect.height // Pango.SCALE

    # Vertical alignment offset
    if valign == "middle":
        y_offset = max((height - text_height) // 2, 0)
    elif valign == "bottom":
        y_offset = max(height - text_height, 0)
    else:
        y_offset = 0

    # Apply color and render
    context.set_source_rgba(color[0] / 255, color[1] / 255, color[2] / 255, 1)
    context.move_to(0, y_offset)
    PangoCairo.show_layout(context, layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img


def render_rotated_text(text, font_family, font_size, color, box_size, angle=90):
    img = render_text(text, font_family, font_size, color, box_size, align="center", valign="middle")
    return img.rotate(angle, expand=True)
