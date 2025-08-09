import argparse
import sys
from layout_engine import CoverLayoutEngine
from text_renderer import verify_font_available

# === Hard Limits (so n8n can enforce before calling this) ===
TITLE_MAX_CHARS = 70
DESC_MAX_CHARS = 400
SPINE_MAX_CHARS = 80

# === Preferred Fonts (installed) ===
PRO_TITLE_FONTS = ["Playfair Display", "EB Garamond", "Libre Baskerville", "DejaVu Serif"]
PRO_BODY_FONTS  = ["Merriweather", "Lora", "Roboto Slab", "DejaVu Serif"]


def pick_font(preferred_list):
    for fam in preferred_list:
        try:
            verify_font_available(fam)
            return fam
        except Exception:
            continue
    return "DejaVu Serif"


def main():
    parser = argparse.ArgumentParser(description="FBNP Cover Text Renderer (Pro Defaults)")
    # Required
    parser.add_argument("--cover", type=str, required=True, help="Path to base cover image")
    parser.add_argument("--output", type=str, default="final_cover.png", help="Output file name")
    parser.add_argument("--title", type=str, required=True, help="Book title (subtitle optional via ':', '-', '—', '|')")
    parser.add_argument("--description", type=str, required=True, help="Back cover description")
    parser.add_argument("--author", type=str, default="", help="Author name")

    # Dimensions
    parser.add_argument("--width", type=int, required=True, help="Full cover width (px)")
    parser.add_argument("--height", type=int, required=True, help="Full cover height (px)")
    parser.add_argument("--spine_width", type=int, required=True, help="Spine width (px)")

    # Optional overrides (you usually don't need to touch these)
    parser.add_argument("--title_size", type=int, default=96)
    parser.add_argument("--desc_size", type=int, default=48)
    parser.add_argument("--spine_size", type=int, default=64)
    parser.add_argument("--title_color", type=str, default="#000000")
    parser.add_argument("--desc_color", type=str, default="#333333")
    parser.add_argument("--debug", action="store_true", help="Draw KDP safe-zone guides")

    args = parser.parse_args()

    # === Limits ===
    if len(args.title) > TITLE_MAX_CHARS:
        sys.exit(f"❌ ERROR: Title exceeds {TITLE_MAX_CHARS} characters (got {len(args.title)}).")
    if len(args.description) > DESC_MAX_CHARS:
        sys.exit(f"❌ ERROR: Description exceeds {DESC_MAX_CHARS} characters (got {len(args.description)}).")
    spine_text = f"{args.title} • {args.author}" if args.author else args.title
    if len(spine_text) > SPINE_MAX_CHARS:
        sys.exit(f"❌ ERROR: Spine text exceeds {SPINE_MAX_CHARS} characters (got {len(spine_text)}).")

    # === Colors ===
    def hex_to_rgb(hx: str):
        hx = hx.lstrip("#")
        return tuple(int(hx[i:i+2], 16) for i in (0, 2, 4))

    title_color = hex_to_rgb(args.title_color)
    desc_color = hex_to_rgb(args.desc_color)

    # === “Professional mode” always on ===
    title_font = pick_font(PRO_TITLE_FONTS)
    body_font = pick_font(PRO_BODY_FONTS)
    # sanity check installed (gives a clear error early if not)
    verify_font_available(title_font)
    verify_font_available(body_font)

    print("\n✨ Professional Defaults:")
    print(f"   ✔ Title Font: {title_font}")
    print(f"   ✔ Body Font:  {body_font}")
    print(f"   ✔ Gradient panel, soft shadow, subtle letter-spacing")
    print(f"   ✔ KDP-safe placement & spine centering\n")

    # === Render ===
    engine = CoverLayoutEngine(args.cover, args.width, args.height, args.spine_width, debug=args.debug)
    print("🔍 Rendering cover...")

    engine.add_text(
        title=args.title,
        description=args.description,
        author=args.author,
        font_family=title_font,
        title_font_size=args.title_size,
        desc_font_size=args.desc_size,
        spine_font_size=args.spine_size,
        title_color=title_color,
        desc_color=desc_color,
        # Always-on pro styling
        add_bg=True,
        line_spacing=10,
        gradient_bg=True,
        text_shadow=True,
        letter_spacing=1.2,
        body_font=body_font,
        blur_bg=True,
    )

    engine.save(args.output)
    print(f"✅ Final cover saved at: {args.output}")


if __name__ == "__main__":
    main()
