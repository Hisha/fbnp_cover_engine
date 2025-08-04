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
        Dynamically scales text down (within min/max rules) if it overflows its safe zone.
        """

        # === Hardcoded Font Size Limits ===
        title_min, title_max = 48, 96
        desc_min, desc_max = 16, 48
        spine_min, spine_max = 32, 64

        # === KDP Safe Zone Settings ===
        bleed = int(0.125 * self.dpi)
        margin = int(0.25 * self.dpi)

        back_width = (self.final_width - self.spine_width) // 2
        front_width = back_width

        # === Safe Zones ===
        front_safe_x = self.spine_width + bleed
        front_safe_width = front_width - (bleed + margin)
        front_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        front_box = (front_safe_width, int(front_safe_height * 0.3))

        back_safe_x = bleed
        back_safe_width = back_width - (bleed + margin)
        back_safe_height = self.final_height - (2 * bleed) - (2 * margin)
        back_box = (back_safe_width, int(back_safe_height * 0.5))

        spine_box = (int(self.spine_width * 0.9), int(self.final_height * 0.8))

        print("📏 Safe zones calculated:")
        print(f"   Title box: {front_box}, Description box: {back_box}, Spine box: {spine_box}")

        # === Render Title ===
        title_img = self._fit_text(
            text=title, font_family=font_family, font_size=title_font_size,
            color=title_color, box_size=front_box, align="center", valign="middle",
            min_size=title_min, max_size=title_max
        )
        title_pos = (front_safe_x + margin, bleed + margin)
        self.cover.paste(title_img, title_pos, title_img)

        # === Render Description ===
        desc_img = self._fit_text(
            text=description, font_family=font_family, font_size=desc_font_size,
            color=desc_color, box_size=back_box, align="left", valign="top",
            min_size=desc_min, max_size=desc_max
        )
        desc_pos = (back_safe_x + margin, bleed + margin)
        self.cover.paste(desc_img, desc_pos, desc_img)

        # === Render Spine Text ===
        spine_text = f"{title} • {author}" if author else title
        spine_img = self._fit_text(
            text=spine_text, font_family=font_family, font_size=spine_font_size,
            color=title_color, box_size=spine_box, align="center", valign="middle",
            min_size=spine_min, max_size=spine_max, rotated=True
        )
        spine_x = (self.final_width // 2) - (spine_img.width // 2)
        spine_y = (self.final_height // 2) - (spine_img.height // 2)
        self.cover.paste(spine_img, (spine_x, spine_y), spine_img)

        return self.cover

    def _fit_text(self, text, font_family, font_size, color, box_size,
                  align, valign, min_size, max_size, rotated=False):
        """
        Dynamically scale text to fit within box. If cannot fit at min_size, raise error.
        """
        max_width, max_height = box_size
        current_size = min(font_size, max_size)
        img, text_w, text_h = render_text(text, font_family, current_size, color, box_size, align, valign)

        while (text_w > max_width or text_h > max_height) and current_size > min_size:
            current_size -= 2
            img, text_w, text_h = render_text(text, font_family, current_size, color, box_size, align, valign)

        if text_w > max_width or text_h > max_height:
            raise ValueError(f"❌ Text too long to fit in safe zone even at min font size {min_size} pt: '{text}'")

        print(f"✅ '{text[:30]}...' fits at {current_size} pt (Box {box_size})")

        if rotated:
            img = img.rotate(90, expand=True)

        return img

    def save(self, path):
        """Save the final cover image at 300 DPI."""
        self.cover.save(path, dpi=(self.dpi, self.dpi))
