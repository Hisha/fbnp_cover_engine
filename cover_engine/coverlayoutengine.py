import argparse
import sys
from layout_engine import CoverLayoutEngine
from text_renderer import verify_font_available

# === Character Limits (hardcoded) ===
TITLE_MAX_CHARS = 70
DESC_MAX_CHARS  = 400
SPINE_MAX_CHARS = 80

# === Preferred font families per style (try in order; fall back gracefully) ===
STYLE_PROFILES = {
    "classic": {
        "title_fonts": ["Playfair Display", "EB Garamond", "Libre Baskerville", "DejaVu Serif"],
        "body_fonts":  ["Merriweather", "Lora", "Roboto Slab", "DejaVu Serif"],
        "letter_spacing": 1.4,
        "title_case": "title",
        "underline": True,
        "frame_border": True,
        "gradient_opacity": 190,
        "blur_radius": 8,
        "shadow": True
    },
    "modern": {
        "title_fonts": ["Montserrat", "Source Sans 3", "Inter", "DejaVu Sans"],
        "body_fonts":  ["Source Serif 4", "Noto Serif", "Merriweather", "DejaVu Serif"],
        "letter_spacing": 0.8,
        "title_case": "sentence",
        "underline": False,
        "frame_border": False,
        "gradient_opacity": 165,
        "blur_radius": 6,
        "shadow": True
    },
    "impact": {
        "title_fonts": ["Oswald", "Bebas Neue", "League Gothic", "DejaVu Sans"],
        "body_fonts":  ["Roboto Slab", "Merriweather", "Noto Serif", "DejaVu Serif"],
        "letter_spacing": 1.0,
        "title_case": "upper",
        "underline": True,
        "frame_border": True,
        "gradient_opacity": 175,
        "blur_radius": 10,
        "shadow": True
    },
}

def pick_first_installed(families):
    """Return the first installed font family from a list."""
    for fam in families:
        try:
            verify_font_available(fam)
            return fam
        except ValueError:
            continue
    # Last-resort fallbacks
    return "DejaVu Serif"

def hex_to_rgb(hex_color: str):
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))

def main():
    parser = argparse.ArgumentParser(description="FBNP Cover Text Renderer CLI")

    # Required
    parser.add_argument("--cover", type=str, required=True, help="Path to base cover image")
    parser.add_argument("--output", type=str, default="final_cover.png", help="Output file")

    parser.add_argument("--title", type=str, required=True, help="Book title")
    parser.add_argument("--description", type=str, required=True, help="Back cover description")
    parser.add_argument("--author", type=str, default="", help="Author name")

    # Fonts & sizes
    parser.add_argument("--font_family", type=str, default="DejaVu Serif",
                        help="Title font (overridden in professional mode unless --style=custom)")
    parser.add_argument("--title_size", type=int, default=96)
    parser.add_argument("--desc_size", type=int, default=48)
    parser.add_argument("--spine_size", type=int, default=64)

    # Colors
    parser.add_argument("--title_color", type=str, default="#000000")
    parser.add_argument("--desc_color", type=str, default="#000000")

    # Dimensions
    parser.add_argument("--width", type=int, required=True)
    parser.add_argument("--height", type=int, required=True)
    parser.add_argument("--spine_width", type=int, required=True)

    # Styling
    parser.add_argument("--add_bg_box", action="store_true", help="Semi-transparent white behind text")
    parser.add_argument("--line_spacing", type=int, default=8)
    parser.add_argument("--debug", action="store_true", help="Draw safe zones")
    parser.add_argument("--gradient", action="store_true", help="Blend gradient behind text")
    parser.add_argument("--shadow", action="store_true", help="Text shadow")
    parser.add_argument("--letter_spacing", type=float, default=0)
    parser.add_argument("--blur_bg", action="store_true", help="Blur art behind text")
    parser.add_argument("--professional", action="store_true", help="Enable pro layout & styling")
    parser.add_argument("--style", choices=list(STYLE_PROFILES.keys()) + ["custom"],
                        default="classic",
                        help="Pro style profile (default: classic). Use 'custom' to keep --font_family.")

    args = parser.parse_args()

    # Validate text lengths
    if len(args.title) > TITLE_MAX_CHARS:
        sys.exit(f"❌ ERROR: Title exceeds {TITLE_MAX_CHARS} characters")
    if len(args.description) > DESC_MAX_CHARS:
        sys.exit(f"❌ ERROR: Description exceeds {DESC_MAX_CHARS} characters")
    spine_text = f"{args.title} • {args.author}" if args.author else args.title
    if len(spine_text) > SPINE_MAX_CHARS:
        sys.exit(f"❌ ERROR: Spine text exceeds {SPINE_MAX_CHARS} characters")

    title_color = hex_to_rgb(args.title_color)
    desc_color  = hex_to_rgb(args.desc_color)

    # Professional preset
    applied = {}
    if args.professional:
        profile_key = args.style
        profile = STYLE_PROFILES.get(profile_key, STYLE_PROFILES["classic"])

        if profile_key != "custom":
            title_font = pick_first_installed(profile["title_fonts"])
            body_font  = pick_first_installed(profile["body_fonts"])
            args.font_family = title_font
        else:
            body_font = args.font_family

        # Turn on pro helpers
        args.gradient = True
        args.shadow   = profile.get("shadow", True)
        args.blur_bg  = True
        args.add_bg_box = True

        if args.letter_spacing == 0:
            args.letter_spacing = profile.get("letter_spacing", 1.2)

        applied = {
            "style": profile_key,
            "title_font": args.font_family,
            "body_font": body_font,
            "letter_spacing": args.letter_spacing,
            "gradient_opacity": profile.get("gradient_opacity", 180),
            "blur_radius": profile.get("blur_radius", 8),
            "underline": profile.get("underline", False),
            "frame_border": profile.get("frame_border", False),
            "title_case": profile.get("title_case", "title"),
        }
    else:
        body_font = args.font_family
        applied = {
            "style": "none",
            "title_font": args.font_family,
            "body_font": body_font,
            "letter_spacing": args.letter_spacing,
            "gradient_opacity": 0,
            "blur_radius": 0,
            "underline": False,
            "frame_border": False,
            "title_case": "as_is",
        }

    # Render
    engine = CoverLayoutEngine(
        args.cover, args.width, args.height, args.spine_width, debug=args.debug
    )

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
        body_font=applied["body_font"],
        blur_bg=args.blur_bg,
        # pro extras
        pro_title_case=applied["title_case"],
        pro_underline=applied["underline"],
        pro_frame_border=applied["frame_border"],
        pro_gradient_opacity=applied["gradient_opacity"],
        pro_blur_radius=applied["blur_radius"],
    )

    engine.save(args.output)
    print(f"✅ Final cover saved at: {args.output}")
