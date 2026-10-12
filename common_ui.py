"""
Shared UI and Font Utilities for Pygame Games
Supports Python 3.14+ (using pygame._freetype when pygame.font circular import occurs)
as well as standard pygame environments.
"""

import os
import json
import pygame

_ft_module = None
_ft_fonts = {}
_pg_fonts = {}
_mode = "unknown"

def _init_font_system():
    global _ft_module, _mode
    if _mode != "unknown":
        return

    # Try pygame._freetype first (fast, reliable, bypasses Python 3.14 font circular import)
    try:
        import pygame._freetype as ft
        ft.init()
        _ft_module = ft
        _mode = "freetype"
        return
    except Exception:
        pass

    # Fallback to standard pygame.font
    try:
        import pygame.font
        pygame.font.init()
        _mode = "font"
        return
    except Exception:
        pass

    _mode = "fallback"


def get_font(size=24):
    """Retrieve or cache a font of specified size."""
    _init_font_system()
    size = max(8, int(size))

    if _mode == "freetype":
        if size not in _ft_fonts:
            try:
                # Use default system font
                _ft_fonts[size] = _ft_module.Font(None, size)
            except Exception:
                _ft_fonts[size] = None
        return _ft_fonts[size]
    elif _mode == "font":
        if size not in _pg_fonts:
            try:
                _pg_fonts[size] = pygame.font.Font(None, size)
            except Exception:
                _pg_fonts[size] = None
        return _pg_fonts[size]
    return None


def draw_text(surface, text, x, y, size=24, color=(255, 255, 255), align="topleft", shadow=None):
    """
    Render text onto surface at (x, y) with alignment:
    align can be 'topleft', 'center', 'midtop', 'topright', 'midbottom', 'midleft', 'midright'.
    Optional shadow: (shadow_color, offset_x, offset_y)
    """
    _init_font_system()
    text_str = str(text)

    # Optional shadow
    if shadow:
        s_color, ox, oy = shadow
        draw_text(surface, text_str, x + ox, y + oy, size=size, color=s_color, align=align)

    if _mode == "freetype":
        font = get_font(size)
        if font:
            try:
                surf, rect = font.render(text_str, color)
                # Position rect
                target_rect = surf.get_rect()
                setattr(target_rect, align, (x, y))
                surface.blit(surf, target_rect)
                return target_rect
            except Exception:
                pass
    elif _mode == "font":
        font = get_font(size)
        if font:
            try:
                surf = font.render(text_str, True, color)
                target_rect = surf.get_rect()
                setattr(target_rect, align, (x, y))
                surface.blit(surf, target_rect)
                return target_rect
            except Exception:
                pass

    # Fallback: draw pixel box outline
    w = len(text_str) * int(size * 0.6)
    h = size
    target_rect = pygame.Rect(0, 0, w, h)
    setattr(target_rect, align, (x, y))
    pygame.draw.rect(surface, color, target_rect, 1)
    return target_rect


def get_text_size(text, size=24):
    """Get the bounding (width, height) of rendered text."""
    _init_font_system()
    text_str = str(text)
    if _mode == "freetype":
        font = get_font(size)
        if font:
            try:
                rect = font.get_rect(text_str)
                return rect.width, rect.height
            except Exception:
                pass
    elif _mode == "font":
        font = get_font(size)
        if font:
            try:
                return font.size(text_str)
            except Exception:
                pass
    return len(text_str) * int(size * 0.6), size


def draw_panel(surface, rect, border_color=(0, 220, 255), bg_color=(15, 20, 35, 220), border_width=2, border_radius=8):
    """Draw a translucent rounded arcade HUD panel."""
    panel_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
    pygame.draw.rect(panel_surf, bg_color, panel_surf.get_rect(), border_radius=border_radius)
    if border_width > 0 and border_color:
        pygame.draw.rect(panel_surf, border_color, panel_surf.get_rect(), width=border_width, border_radius=border_radius)
    surface.blit(panel_surf, rect.topleft)


def load_high_score(filepath, default=0):
    """Safely load high score from a JSON file."""
    try:
        if os.path.exists(filepath):
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return int(data.get("high_score", default))
    except Exception:
        pass
    return default


def save_high_score(filepath, score):
    """Safely save high score to a JSON file."""
    try:
        os.makedirs(os.path.dirname(os.path.abspath(filepath)), exist_ok=True)
        current = load_high_score(filepath, 0)
        if score > current:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump({"high_score": int(score)}, f, indent=2)
            return True
    except Exception:
        pass
    return False
