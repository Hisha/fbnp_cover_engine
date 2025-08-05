import argparse
import sys
from layout_engine import CoverLayoutEngine
from text_renderer import verify_font_available

# === Character Limits (Hardcoded) ===
TITLE_MAX_CHARS = 70
DESC_MAX_CHARS = 400
SPINE_MAX_CHARS = 80


def main():
    parser = argparse.ArgumentParser(description="FBNP Cover Text Renderer CLI")

    # === Required Args ===
    parser.add_argument("--cover", type=str, required=True, help="Path to base cover image")
    parser.add_argument("--output", type=str, default="final_cover.png", help="Output file name")

    parser.add_argument("--title", type=str, required=True, help="Book title")
    parser.add_argument("--description", type=str, required=True, help="Back cover description text")
    parser.add_argument("--author", type=str, default="", help="Author name")

    parser.add_argument("--font_family", type=str, required=True, help="Font family (must be installed)")
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

    # === Verify font availability ===
    verify_font_available(args.font_family)
    print(f"✅ Font '{args.font_family}' is available.")

    # === Apply Professional Preset if enabled ===
    if args.professional:
        args.gradient = True
        args.shadow = True
        args.add_bg_box = True
        if args.letter_spacing == 0:  # If user didn't override
            args.letter_spacing = 1.2
        print("\n✨ Professional Mode Enabled:")
        print("   ✔ Gradient background")
        print("   ✔ Text shadow")
        print("   ✔ Background boxes")
        print("   ✔ Letter spacing applied\n")

    # === Print Applied Settings Summary ===
    print("\n📏 **Character Limit Guidelines**")
    print(f"   Title: {TITLE_MAX_CHARS} chars max")
    print(f"   Description: {DESC_MAX_CHARS} chars max")
    print(f"   Spine: {SPINE_MAX_CHARS} chars max\n")

    print("🎨 **Applied Styling**")
    print(f"   Gradient: {args.gradient}")
    print(f"   Shadow: {args.shadow}")
    print(f"   Background Box: {args.add_bg_box}")
    print(f"   Letter Spacing: {args.letter_spacing}")
    print(f"   Debug Mode: {args.debug}\n")

    # === Apply text ===
    engine = CoverLayoutEngine(args.cover, args.width, args.height, args.spine_width, debug=args.debug)
    print("🔍 Applying text to cover...")

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
        text_shadow=args.shadow
    )

    engine.save(args.output)
    print(f"✅ Final cover saved at: {args.output}")


if __name__ == "__main__":
    main()
