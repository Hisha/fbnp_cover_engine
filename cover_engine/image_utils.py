from PIL import Image

def resize_with_aspect_ratio(image, target_width, target_height):
    image.thumbnail((target_width, target_height), Image.LANCZOS)
    return image

def add_bleed(image, bleed_size):
    # Adds bleed margin to image
    pass
