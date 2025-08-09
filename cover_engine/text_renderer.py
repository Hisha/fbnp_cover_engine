import subprocess
import gi

gi.require_version("Pango", "1.0")
gi.require_version("PangoCairo", "1.0")
from gi.repository import Pango, PangoCairo
import cairo
from PIL import Image


# ===== Font Verification =====
def verify_font_available(font_family: str):
    """
    Check if the given font family is available on the system via fontconfig.
    Raises ValueError if not found.
    """
    result = subprocess.run(["fc-list", font_family], capture_output=True, text=True)
    if not result.stdout.strip():
        raise ValueError(f"❌ Font '{font_family}' is not installed. Please install it and run again.")


# ===== Render Text with Advanced Styling =====
def render_text(
    text: str,
    font_family: str,
    font_size: int,
    color: tuple,
    box_size: tuple,
    align: str = "left",
    valign: str = "top",
    spacing: int = 0,
    bold: bool = False,
    italic: bool = False,
    add_bg: bool = False,
    gradient_bg: bool = False,
    rounded_bg: bool = True,
    letter_spacing: float = 0,
    text_shadow: bool = True,
    rotated: bool = False,
    small_caps: bool = False,
    justify: bool = False,
    padding_px: int = 12,
):
    """
    Draw styled, wrapped text into a transparent RGBA image.

    Features:
      - Word/char wrapping in a fixed box
      - Horizontal alignment (left/center/right)
      - Vertical alignment (top/middle/bottom)
      - Optional justification for body text
      - Optional gradient or semi-transparent rounded panel behind text
      - Optional soft shadow
      - Letter spacing, small-caps simulation
      - Rotation for spine text
    """
    width, height = box_size
    surface = cairo.ImageSurface(cairo.FORMAT_ARGB32, width, height)
    ctx = cairo.Context(surface)

    # --- Background panel (improves readability on busy art) ---
    if gradient_bg or add_bg:
        # Panel area (respect padding so text doesn't kiss the edges)
        panel_x = 0
        panel_y = 0
        panel_w = width
        panel_h = height

        radius = 14 if rounded_bg else 0
        _rounded_rect(ctx, panel_x, panel_y, panel_w, panel_h, radius)

        if gradient_bg:
            grad = cairo.LinearGradient(0, panel_y, 0, panel_y + panel_h)
            # subtle top brighter -> bottom a hair darker
            grad.add_color_stop_rgba(0, 1, 1, 1, 0.85)
            grad.add_color_stop_rgba(1, 0.95, 0.95, 0.95, 0.85)
            ctx.set_source(grad)
        else:
            ctx.set_source_rgba(1, 1, 1, 0.78)

        ctx.fill()

    # --- Pango layout ---
    layout = PangoCairo.create_layout(ctx)

    # Keep text inside a padded area for nicer margins
    text_area_w = max(0, width - 2 * padding_px)
    layout.set_width(text_area_w * Pango.SCALE)
    layout.set_wrap(Pango.WrapMode.WORD_CHAR)

    if small_caps:
        text = text.upper()
        # Knock down size slightly to simulate true small-caps feel
        font_size = max(8, int(font_size * 0.9))

    layout.set_text(text, -1)

    # Font
    font_desc = Pango.FontDescription()
    font_desc.set_family(font_family)
    font_desc.set_size(font_size * Pango.SCALE)
    if bold:
        font_desc.set_weight(Pango.Weight.BOLD)
    if italic:
        font_desc.set_style(Pango.Style.ITALIC)
    layout.set_font_description(font_desc)

    # Line spacing
    if spacing > 0:
        layout.set_spacing(int(spacing * Pango.SCALE))

    # Letter spacing
    attrs = Pango.AttrList()
    if letter_spacing > 0:
        attrs.insert(Pango.attr_letter_spacing_new(int(letter_spacing * Pango.SCALE)))
    layout.set_attributes(attrs)

    # Horizontal alignment
    if align == "center":
        layout.set_alignment(Pango.Alignment.CENTER)
    elif align == "right":
        layout.set_alignment(Pango.Alignment.RIGHT)
    else:
        layout.set_alignment(Pango.Alignment.LEFT)

    # Justify mostly for description/body text
    layout.set_justify(bool(justify and align == "left"))

    # Measure logical extents
    ink_rect, logical_rect = layout.get_extents()
    text_w = logical_rect.width // Pango.SCALE
    text_h = logical_rect.height // Pango.SCALE

    # Vertical alignment (compute Y offset)
    if valign == "middle":
        y_offset = max((height - text_h) // 2, 0)
    elif valign == "bottom":
        y_offset = max(height - text_h, 0)
    else:
        y_offset = padding_px  # top: give it the same padding

    # X offset (padding & alignment)
    x_offset = padding_px

    # --- Soft shadow for legibility ---
    if text_shadow:
        shadow_dx, shadow_dy = 2, 2
        ctx.set_source_rgba(0, 0, 0, 0.45)
        ctx.move_to(x_offset + shadow_dx, y_offset + shadow_dy)
        PangoCairo.show_layout(ctx, layout)

    # --- Main text ---
    r, g, b = color
    ctx.set_source_rgba(r / 255.0, g / 255.0, b / 255.0, 1.0)
    ctx.move_to(x_offset, y_offset)
    PangoCairo.show_layout(ctx, layout)

    # Convert to PIL
    buf = surface.get_data()
    img = Image.frombuffer("RGBA", (width, height), buf, "raw", "BGRA", 0, 1)

    if rotated:
        img = img.rotate(90, expand=True)

    return img


def _rounded_rect(ctx: cairo.Context, x: int, y: int, w: int, h: int, r: int):
    """Draw a rounded rectangle path on the given context."""
    if r <= 0:
        ctx.rectangle(x, y, w, h)
        return
    # Clamp radius
    r = min(r, int(min(w, h) / 2))
    # Path
    ctx.new_path()
    ctx.arc(x + w - r, y + r, r, -90 * (3.14159 / 180.0), 0)
    ctx.arc(x + w - r, y + h - r, r, 0, 90 * (3.14159 / 180.0))
    ctx.arc(x + r, y + h - r, r, 90 * (3.14159 / 180.0), 180 * (3.14159 / 180.0))
    ctx.arc(x + r, y + r, r, 180 * (3.14159 / 180.0), 270 * (3.14159 / 180.0))
    ctx.close_path()
