"""UI theme and color constants for a clean, modern look."""

# Color palette - warm, inviting tones
COLORS = {
    "bg_primary": "#1a1a2e",        # Deep navy background
    "bg_secondary": "#16213e",      # Slightly lighter navy
    "bg_card": "#0f3460",           # Card background
    "bg_input": "#1a1a2e",          # Input field background
    "accent": "#e94560",            # Warm rose accent
    "accent_hover": "#c73e54",      # Darker rose for hover
    "accent_soft": "#533483",       # Soft purple
    "text_primary": "#ffffff",      # White text
    "text_secondary": "#a0a0b8",    # Muted text
    "text_muted": "#6c6c80",        # Very muted text
    "success": "#4ecca3",           # Green for success
    "warning": "#ffc107",           # Yellow for warnings
    "border": "#2a2a4a",            # Subtle border
    "star_filled": "#ffc107",       # Gold star
    "star_empty": "#3a3a5a",        # Empty star
}

# Font configuration
FONTS = {
    "heading_large": ("SF Pro Display", 28, "bold"),
    "heading": ("SF Pro Display", 22, "bold"),
    "subheading": ("SF Pro Display", 16, "bold"),
    "body": ("SF Pro Text", 14),
    "body_bold": ("SF Pro Text", 14, "bold"),
    "small": ("SF Pro Text", 12),
    "tiny": ("SF Pro Text", 11),
    "emoji": ("Apple Color Emoji", 20),
}

# Fallback fonts for systems without SF Pro
FONT_FALLBACKS = {
    "SF Pro Display": ["Helvetica Neue", "Helvetica", "Arial"],
    "SF Pro Text": ["Helvetica Neue", "Helvetica", "Arial"],
}

# Layout constants
LAYOUT = {
    "window_width": 800,
    "window_height": 650,
    "padding": 20,
    "card_padding": 16,
    "corner_radius": 12,
    "button_height": 40,
    "input_height": 38,
}
