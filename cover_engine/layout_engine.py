from PIL import Image, ImageDraw
from text_renderer import render_text, render_rotated_text

class CoverLayoutEngine:
    def __init__(self, cover_image_path, final_width, final_height, spine_width):
        self.cover = Image.open(cover_image_path).convert("RGBA")
        self.final_width = final_width
        self.final_height = final_height
        self.spine_width = spine_width
        self.dpi = 300

    def add_text(self, title, description, author=None,
                 font_path="Arial.ttf", title_color=(0, 0, 0), desc_color=(0, 0, 0)):
        """
        Places title, spine text, and description onto the cover image.
        Keeps proper safe margins for KDP.
        """
        # === Safe zone constants (in pixels at 300 DPI)
        bleed = int(0.125 * self.dpi)  # 0.125" bleed
        margin = int(0.25 * self.dpi)  # 0.25" margin inside safe zone

        # === Calculate regions
        # Front cover box
        front_x = self.spine_width + bleed
        front_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        front_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_width, int(front_height * 0.3))  # Title uses top 30%

        # Back cover box
        back_x = bleed
        back_width = (self.final_width - self.spine_width) // 2 - bleed - margin
        back_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_width, int(back_height * 0.5))  # Description uses 50%

        # Spine box
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        # === Render Title for Front Cover
        title_img = render_text(title, font_path, font_size=96, color=title_color, box_size=front_box, align="center")
        title_position = (front_x + margin, margin + bleed)
        self.cover.paste(title_img, title_position, title_img)

        # === Render Description for Back Cover
        desc_img = render_text(description, font_path, font_size=48, color=desc_color, box_size=back_box, align="left")
        desc_position = (back_x + margin, margin + bleed)
        self.cover.paste(desc_img, desc_position, desc_img)

        # === Render Spine Text (Title or Author)
        spine_text = title if author is None else f"{title} • {author}"
        spine_img = render_rotated_text(spine_text, font_path, font_size=64, color=title_color, box_size=spine_box)
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def save(self, path):
        self.cover.save(path, dpi=(self.dpi, self.dpi))
