from PIL import Image
from text_renderer import render_text, render_rotated_text

class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width, dpi=300):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = dpi

    def add_text(self, title, description, author,
                 font_family, title_font_size, desc_font_size, spine_font_size,
                 title_color, desc_color):
        """
        Places title, spine text, and description onto the cover image using Pango.
        All font sizes and colors must be explicitly provided (no defaults).
        """
        # === Safe zone constants (in pixels at 300 DPI)
        bleed = int(0.125 * self.dpi)  # 0.125" bleed
        margin = int(0.25 * self.dpi)  # 0.25" margin inside safe zone

        # === Calculate regions
        # Front cover box (title at top 30%)
        front_x = self.spine_width + bleed
        front_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        front_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_width, int(front_height * 0.3))

        # Back cover box (description at top 50%)
        back_x = bleed
        back_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        back_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_width, int(back_height * 0.5))

        # Spine box
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        # === Render Title on Front Cover
        title_img = render_text(title, font_family, font_size=title_font_size,
                                color=title_color, box_size=front_box, align="center")
        title_position = (front_x + margin, margin + bleed)
        self.cover.paste(title_img, title_position, title_img)

        # === Render Description on Back Cover
        desc_img = render_text(description, font_family, font_size=desc_font_size,
                               color=desc_color, box_size=back_box, align="left")
        desc_position = (back_x + margin, margin + bleed)
        self.cover.paste(desc_img, desc_position, desc_img)

        # === Render Spine Text (Title + Author)
        spine_text = f"{title} • {author}" if author else title
        spine_img = render_rotated_text(spine_text, font_family,
                                        font_size=spine_font_size, color=title_color, box_size=spine_box, angle=90)
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
