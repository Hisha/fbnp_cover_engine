from PIL import Image
from text_renderer import render_text, render_rotated_text


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
        Places title, spine text, and description onto the cover image with strict KDP safe zones.
        - Bleed: 0.125" on all sides
        - Safe zone margin: 0.25" inside the bleed
        Dynamically scales text to fit inside its safe zone.
        """

        # === KDP Safe Zone Settings ===
        bleed = int(0.125 * self.dpi)  # 0.125" bleed area in pixels
        margin = int(0.25 * self.dpi)  # 0.25" margin inside the bleed

        # === Split Cover ===
        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # === Safe Zones ===
        # Front Title Area (top 30% of front safe zone)
        front_safe_x = self.spine_width + bleed
        front_safe_width = front_width - (bleed + margin)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))

        # Back Description Area (top 50% of back safe zone)
        back_safe_x = bleed
        back_safe_width = back_width - (bleed + margin)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))

        # Spine Area
        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        # === Render Title on Front ===
        title_img = self._render_scaled_text(
            text=title,
            font_family=font_family,
            font_size=title_font_size,
            color=title_color,
            box_size=front_box,
            align="center",
            valign="middle"
        )
        title_pos = (front_safe_x + margin, bleed + margin)
        self.cover.paste(title_img, title_pos, title_img)

        # === Render Description on Back ===
        desc_img = self._render_scaled_text(
            text=description,
            font_family=font_family,
            font_size=desc_font_size,
            color=desc_color,
            box_size=back_box,
            align="left",
            valign="top"
        )
        desc_pos = (back_safe_x + margin, bleed + margin)
        self.cover.paste(desc_img, desc_pos, desc_img)

        # === Render Spine Text ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = self._render_scaled_text(
            text=spine_text,
            font_family=font_family,
            font_size=spine_font_size,
            color=title_color,
            box_size=spine_box,
            align="center",
            valign="middle",
            rotated=True
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def _render_scaled_text(self, text, font_family, font_size, color, box_size, align, valign, rotated=False):
        """
        Render text and scale it down dynamically if it overflows the box.
        """
        img = render_text(text, font_family, font_size, color, box_size, align, valign)
        max_width, max_height = box_size

        # If overflow, reduce font size iteratively
        while (img.width > max_width or img.height > max_height) and font_size > 12:
            font_size -= 4
            img = render_text(text, font_family, font_size, color, box_size, align, valign)

        if rotated:
            img = img.rotate(90, expand=True)

        return img

    def save(self, path):
        """Save the final cover image with 300 DPI."""
        self.cover.save(path, dpi=(self.dpi, self.dpi))
