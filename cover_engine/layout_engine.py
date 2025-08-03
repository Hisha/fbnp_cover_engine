from PIL import Image
from text_renderer import render_text, render_rotated_text, resolve_font

class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300

    def add_text(self, title, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color):
        """
        Places title, spine text, and description onto the cover image with custom font sizes.
        """

        # ✅ Resolve font to ensure it's available (returns family name)
        resolved_font = resolve_font(font_family)

        # === Safe zone constants ===
        bleed = int(0.125 * self.dpi)  # 0.125" bleed
        margin = int(0.25 * self.dpi)  # 0.25" margin

        # === Calculate regions ===
        # Front cover (title top 30%)
        front_x = self.spine_width + bleed
        front_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        front_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_width, int(front_height * 0.3))

        # Back cover (description top 50%)
        back_x = bleed
        back_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        back_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_width, int(back_height * 0.5))

        # Spine text box
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        # === Render Title ===
        title_img = render_text(title, resolved_font, title_font_size, title_color, front_box, "center")
        self.cover.paste(title_img, (front_x + margin, margin + bleed), title_img)

        # === Render Description ===
        desc_img = render_text(description, resolved_font, desc_font_size, desc_color, back_box, "left")
        self.cover.paste(desc_img, (back_x + margin, margin + bleed), desc_img)

        # === Render Spine Text ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = render_rotated_text(spine_text, resolved_font, spine_font_size, title_color, spine_box)
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def save(self, path):
        """Save the final cover image with proper DPI."""
        self.cover.save(path, dpi=(self.dpi, self.dpi))
