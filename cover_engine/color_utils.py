def get_contrast_color(bg_color):
    """
    Returns a contrasting text color (black or white) for a given background color.
    """
    r, g, b = bg_color
    brightness = (r * 299 + g * 587 + b * 114) / 1000
    return (0, 0, 0) if brightness > 128 else (255, 255, 255)
