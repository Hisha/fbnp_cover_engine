import argparse
from layout_engine import CoverLayoutEngine
from text_renderer import verify_or_download_font  # ✅ Updated to use new logic


def main():
    parser = argparse.ArgumentParser(description="FBNP Cover Text Renderer CLI")

    # === Required Args ===
    parser.add_argument("--cover", type=str, required=True, help="Path to base cover image")
    parser.add_argument("--output", type=str, default="final_cover.png", help="Output file name")

    parser.add_argument("--title", type=str, required=True, help="Book title")
    parser.add_argument("--description", type=str, required=True, help="Back cover description text")
    parser.add_argument("--author", type=str, default="", help="Author name")

    parser.add_argument("--font_family", type=str, required=True, help="Font family (e.g., Arial, Lobster)")
    parser.add_argument("--title_size", type=int, default=96, help="Font size for title text")
    parser.add_argument("--desc_size", type=int, default=48, help="Font size for description text")
    parser.add_argument("--spine_size", type=int, default=64, help="Font size for spine text")

    parser.add_argument("--title_color", type=str, default="#000000", help="Hex color for title text")
    parser.add_argument("--desc_color", type=str, default="#000000", help="Hex color for description text")

    parser.add_argument("--width", type=int, required=True, help="Final cover width in pixels")
    parser.add_argument("--height", type=int, required=True, help="Final cover height in pixels")
    parser.add_argument("--spine_width", type=int, required=True, help="Spine width in pixels")

    args = parser.parse_args()

    # === Convert colors from hex to RGB ===
    def hex_to_rgb(hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

    title_color = hex_to_rgb(args.title_color)
    desc_color = hex_to_rgb(args.desc_color)

    # === Verify or download font ===
    font_family = verify_or_download_font(args.font_family)
    print(f"✅ Using font: {font_family}")

    # === Initialize engine ===
    engine = CoverLayoutEngine(args.cover, args.width, args.height, args.spine_width)

    # === Apply text ===
    print("🔍 Applying text to cover...")
    final_cover = engine.add_text(
        title=args.title,
        description=args.description,
        author=args.author,
        font_family=font_family,  # ✅ This is now Pango-compatible
        title_font_size=args.title_size,
        desc_font_size=args.desc_size,
        spine_font_size=args.spine_size,
        title_color=title_color,
        desc_color=desc_color
    )

    # === Save final cover ===
    engine.save(args.output)
    print(f"✅ Final cover saved at: {args.output}")


if __name__ == "__main__":
    main()
