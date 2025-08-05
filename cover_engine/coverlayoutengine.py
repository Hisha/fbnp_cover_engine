import argparse
import sys
from layout_engine import CoverLayoutEngine
from text_renderer import verify_font_available

# === Character Limits (Hardcoded) ===
TITLE_MAX_CHARS = 70
DESC_MAX_CHARS = 400
SPINE_MAX_CHARS = 80

# === Preferred Fonts for Professional Mode ===
PRO_TITLE_FONTS = ["Playfair Display", "EB Garamond", "Libre Baskerville"]
PRO_BODY_FONTS = ["Merriweather", "Lora", "Roboto Slab", "DejaVu Serif"]

def pick_font(preferred_fonts):
    for font in preferred_fonts:
        try:
            verify_font_available(font)
            return font
        except ValueError:
            continue
    return "DejaVu Serif"  # Fallback if none are installed

def main():
    parser = argparse.ArgumentParser(description="FBNP Cover Text Renderer CLI")

    # === Required Args ===
    parser.add_argument("--cover", type=str, required=True, help="Path to base cover image")
    parser.add_argument("--output", type=str, default="final_cover.png", help="Output file name")

    parser.add_argument("--title", type=str, required=True, help="Book title")
    parser.add_argument("--description", type=str, required=True, help="Back cover description text")
    parser.add_argument("--author", type=str, default="", help="Author name")

    parser.add_argument("--font_family", type=str, default="DejaVu Serif", help="Font family (will be overridden in professional mode)")
    parser.add_argument("--title_size", type=int, default=96, help="Font size for title text")
    parser.add_argument("--desc_size", type=int, default=48, help="Font size for description text")
    parser.add_argument("--spine_size", type=int, default=64, help="Font size for spine text")

    parser.add_argument("--title_color", type=str, default="#000000", help="Hex color for title text")
    parser.add_argument("--desc_color", type=str, default="#000000", help="Hex color for description text")

    parser.add_argument("--width", type=int, required=True, help="Final cover width in pixels")
    parser.add_argument("--height", type=int, required=True, help="Final cover height in pixels")
    parser.add_argument("--spine_width", type=int, required=True, help="Spine width in pixels")

    # === Optional Styling Features ===
    parser.add_argument("--add_bg_box", action="store_true", help="Add semi-transparent white box behind text")
    parser.add_argument("--line_spacing", type=int, default=8, help="Line spacing for description text (in px)")
    parser.add_argument("--debug", action="store_true", help="Draw debug rectangles for safe zones")
    parser.add_argument("--gradient", action="store_true", help="Add gradient overlay behind text areas")
    parser.add_argument("--shadow", action="store_true", help="Add text shadow for readability")
    parser.add_argument("--letter_spacing", type=float, default=0, help="Custom letter spacing (optional)")
    parser.add_argument("--professional", action="store_true", help="Enable all pro settings for best quality")

    args = parser.parse_args()

    # === Validate character limits ===
    if len(args.title) > TITLE_MAX_CHARS:
        print(f"❌ ERROR: Title exceeds {TITLE_MAX_CHARS} characters. Current length: {len(args.title)}")
        sys.exit(1)

    if len(args.description) > DESC_MAX_CHARS:
        print(f"❌ ERROR: Description exceeds {DESC_MAX_CHARS} characters. Current length: {len(args.description)}")
        sys.exit(1)

    spine_text = f"{args.title} • {args.author}" if args.author else args.title
    if len(spine_text) > SPINE_MAX_CHARS:
        print(f"❌ ERROR: Spine text exceeds {SPINE_MAX_CHARS} characters. Current length: {len(spine_text)}")
        sys.exit(1)

    # === Convert colors ===
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    title_color = hex_to_rgb(args.title_color)
    desc_color = hex_to_rgb(args.desc_color)

    # === Apply Professional Preset ===
    if args.professional:
        args.gradient = True
        args.shadow = True
        args.add_bg_box = True
        if args.letter_spacing == 0:
            args.letter_spacing = 1.5
        args.font_family = pick_font(PRO_TITLE_FONTS)
        body_font = pick_font(PRO_BODY_FONTS)
        print("\n✨ Professional Mode Enabled:")
        print(f"   ✔ Title Font: {args.font_family}")
        print(f"   ✔ Body Font: {body_font}")
        print(f"   ✔ Gradient + Shadow + BG Boxes")
        print(f"   ✔ Letter Spacing: {args.letter_spacing}\n")
    else:
        body_font = args.font_family

    # === Print Styling Summary ===
    print("\n📏 Character Limits:")
    print(f"   Title: {TITLE_MAX_CHARS} chars max")
    print(f"   Description: {DESC_MAX_CHARS} chars max")
    print(f"   Spine: {SPINE_MAX_CHARS} chars max\n")

    # === Render ===
    engine = CoverLayoutEngine(args.cover, args.width, args.height, args.spine_width, debug=args.debug)
    print("🔍 Rendering cover...")

    engine.add_text(
        title=args.title,
        description=args.description,
        author=args.author,
        font_family=args.font_family,
        title_font_size=args.title_size,
        desc_font_size=args.desc_size,
        spine_font_size=args.spine_size,
        title_color=title_color,
        desc_color=desc_color,
        add_bg=args.add_bg_box,
        line_spacing=args.line_spacing,
        gradient_bg=args.gradient,
        text_shadow=args.shadow,
        letter_spacing=args.letter_spacing,
        body_font=body_font
    )

    engine.save(args.output)
    print(f"✅ Final cover saved at: {args.output}")


if __name__ == "__main__":
    main()
