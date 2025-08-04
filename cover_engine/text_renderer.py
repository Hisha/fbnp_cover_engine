import subprocess
import gi
gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image

# ===== Font Verification =====
def verify_font_available(font_family):
    try:
        result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
        if not result.stdout.strip():
            raise ValueError(f"❌ Font '{font_family}' is not installed. Please install it and run again.")
    except FileNotFoundError:
        raise RuntimeError("❌ 'fc-list' command not found. Install fontconfig to check fonts.")


# ===== Render Text with Styling =====
def render_text(text, font_family, font_size, color, box_size, align="left", valign="top",
                spacing=0, bold=False, italic=False, add_bg=False, gradient_bg=False,
                letter_spacing=0, text_shadow=False):
    """
    Render styled text onto a Cairo surface and return as a PIL Image.
    Features:
      - Background box or gradient
      - Text shadow
      - Letter spacing
      - Bold / Italic
      - Horizontal & vertical alignment
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    context = cairo.Context(surface)

    # === Background ===
    if gradient_bg:
        # Vertical gradient from white to light gray
        grad = cairo.LinearGradient(0, 0, 0, height)
        grad.add_color_stop_rgba(0, 1, 1, 1, 0.9)
        grad.add_color_stop_rgba(1, 0.9, 0.9, 0.9, 0.9)
        context.set_source(grad)
        context.rectangle(0, 0, width, height)
        context.fill()
    elif add_bg:
        context.set_source_rgba(1, 1, 1, 0.75)  # Semi-transparent white
        context.rectangle(0, 0, width, height)
        context.fill()

    # === Create Pango Layout ===
    layout = PangoCairo.create_layout(context)
    layout.set_width(width * Pango.SCALE)
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)
    layout.set_text(text, -1)

    # === Font Settings ===
    font_desc = Pango.FontDescription()
    font_desc.set_family(font_family)
    font_desc.set_size(font_size * Pango.SCALE)
    if bold:
        font_desc.set_weight(Pango.Weight.BOLD)
    if italic:
        font_desc.set_style(Pango.Style.ITALIC)
    layout.set_font_description(font_desc)

    # Line Spacing
    if spacing > 0:
        layout.set_spacing(int(spacing * Pango.SCALE))

    # Letter Spacing
    attrs = Pango.AttrList()
    if letter_spacing > 0:
        attrs.insert(Pango.attr_letter_spacing_new(letter_spacing * Pango.SCALE))
    layout.set_attributes(attrs)

    # Horizontal Alignment
    if align == "center":
        layout.set_alignment(Pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(Pango.Alignment.RIGHT)
    else:
        layout.set_alignment(Pango.Alignment.LEFT)

    # === Calculate Vertical Offset ===
    ink_rect, logical_rect = layout.get_extents()
    text_height = logical_rect.height // Pango.SCALE
    if valign == "middle":
        y_offset = max((height - text_height) // 2, 0)
    elif valign == "bottom":
        y_offset = max(height - text_height, 0)
    else:
        y_offset = 0

    # === Draw Shadow if enabled ===
    if text_shadow:
        shadow_offset = 4
        context.set_source_rgba(0, 0, 0, 0.5)  # semi-transparent black
        context.move_to(shadow_offset, y_offset + shadow_offset)
        PangoCairo.show_layout(context, layout)

    # === Draw Main Text ===
    context.set_source_rgba(color[0]/255, color[1]/255, color[2]/255, 1)
    context.move_to(0, y_offset)
    PangoCairo.show_layout(context, layout)

    # Convert to PIL Image
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)
    return img


def render_rotated_text(text, font_family, font_size, color, box_size, angle=90,
                        bold=False, italic=False, add_bg=False, gradient_bg=False,
                        letter_spacing=0, text_shadow=False):
    img = render_text(text, font_family, font_size, color, box_size,
                      align="center", valign="middle",
                      bold=bold, italic=italic,
                      add_bg=add_bg, gradient_bg=gradient_bg,
                      letter_spacing=letter_spacing, text_shadow=text_shadow)
    return img.rotate(angle, expand=True)
