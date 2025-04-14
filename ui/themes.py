# UI color scheme
COLORS = {
    "primary": "#172f66",      # Dark blue - primary background
    "secondary": "#0096F7",    # Light blue - secondary elements
    "accent": "#FF5900",       # Orange - active buttons and highlights
    "background": "#E0E1E1",   # Light gray - main background
    "text_light": "#FFFFFF",   # White - text on dark backgrounds
    "text_dark": "#000000",    # Black - text on light backgrounds
    "highlight": "#f46206",    # Bright orange - important elements
    "bezel": "#CBCBCB",        # Medium gray - borders and bezels
    "success": "#28a745",      # Green - success messages/buttons
    "error": "#dc3545",        # Red - error messages
}

# Font configurations
FONTS = {
    "header": ("ANTON", 35, "bold"),
    "subheader": ("ANTON", 25, "bold"),
    "button": ("ANTON", 15, "bold"),
    "label": ("ANTON", 12, "bold"),
    "small_label": ("ANTON", 8, "bold"),
    "entry": ("Arial", 12),
    "small_entry": ("Arial", 10),
}

# Widget style configurations
STYLE = {
    "button": {
        "background": COLORS["primary"],
        "foreground": COLORS["text_light"],
        "active_foreground": COLORS["accent"],
        "font": FONTS["button"],
        "relief": "raised",
    },
    "frame": {
        "background": COLORS["primary"],
        "highlight_background": COLORS["bezel"],
        "highlight_thickness": 2,
    },
    "content_frame": {
        "background": COLORS["secondary"],
        "highlight_background": COLORS["accent"],
        "highlight_thickness": 4,
    },
    "label": {
        "background": COLORS["primary"],
        "foreground": COLORS["text_light"],
        "font": FONTS["label"],
    },
    "entry": {
        "font": FONTS["entry"],
    },
}

def apply_button_style(button, active=False):
    """Apply the standard button style to a button widget"""
    button.config(
        bg=STYLE["button"]["background"],
        fg=STYLE["button"]["active_foreground"] if active else STYLE["button"]["foreground"],
        font=STYLE["button"]["font"],
        relief=STYLE["button"]["relief"],
    )

def apply_frame_style(frame):
    """Apply the standard frame style to a frame widget"""
    frame.config(
        background=STYLE["frame"]["background"],
        highlightbackground=STYLE["frame"]["highlight_background"],
        highlightthickness=STYLE["frame"]["highlight_thickness"],
    )