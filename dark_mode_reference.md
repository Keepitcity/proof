# Dark Mode Reference - Saved for Future Re-implementation

This file preserves all dark mode code and logic so it can be added back later.

**Removed from navbar on:** 2026-02-13
**Reason:** Causing too many UI issues during development. Will re-add when stable.

---

## Dark Mode Color Theme (DARK_MODE dict in qa_tool.py)

```python
DARK_MODE = {
    "bg": "#000000",              # Pure black background
    "bg_secondary": "#111111",    # Slightly lighter black
    "card": "#161616",            # Dark gray cards
    "card_hover": "#1C1C1C",      # Card hover state
    "border": "#2D2D2D",          # Dark borders
    "border_strong": "#404040",   # Stronger borders
    "text": "#FFFFFF",            # Pure white text
    "text_secondary": "#A1A1A1",  # Gray text
    "text_muted": "#6B6B6B",      # Muted text
    "accent": "#FFFFFF",          # White accent
    "accent_hover": "#E5E5E5",    # Accent hover
    "success": "#06C167",         # Green stays same
    "error": "#FF4D4D",           # Brighter red for dark
    "warning": "#FFB800",         # Brighter orange for dark
    "navbar": "#000000",          # Black navbar
    "navbar_border": "#2D2D2D",   # Navbar border
}
```

## Toggle HTML (was in navbar)

```python
# Dark mode toggle knob position
knob_left = "24px" if is_dark else "2px"

# Toggle link
<a href="{build_theme_url('light' if is_dark else 'dark')}" target="_parent" style="text-decoration: none; display: block; margin-left: 12px;">
    <div class="proof-toggle" style="background: {theme['bg_secondary']}; border: 1px solid {theme['border']}; width: 48px; height: 26px; border-radius: 13px; position: relative; cursor: pointer;">
        <div style="position: absolute; top: 2px; left: {knob_left}; width: 20px; height: 20px; border-radius: 50%; background: {'#FFFFFF' if is_dark else '#000000'}; transition: left 0.3s ease;"></div>
    </div>
</a>
```

## Theme URL Builder

```python
def build_theme_url(new_theme):
    """Build URL that switches theme"""
    params = st.query_params.to_dict()
    params['theme'] = new_theme
    return f"?{'&'.join(f'{k}={v}' for k, v in params.items())}"
```

## Session State Init

```python
if 'dark_mode' not in st.session_state:
    st.session_state.dark_mode = False

# Theme param handling
if theme_param == 'dark':
    st.session_state.dark_mode = True
elif theme_param == 'light':
    st.session_state.dark_mode = False
```

## CSS for Toggle

```css
.proof-toggle {
    background: {theme['bg_secondary']};
    border: 1px solid {theme['border']};
    width: 48px;
    height: 26px;
    border-radius: 13px;
    position: relative;
    cursor: pointer;
}
```

## Icon Inversion for Dark Mode

```css
/* In dark mode, invert neutral icons */
.proof-icon {
    filter: invert(1);  /* when dark mode bg is black */
}
```

## Notes for Re-implementation
- The DARK_MODE dict and get_theme_colors() function should stay in qa_tool.py (they don't hurt anything)
- Just need to add the toggle back to the navbar
- Make sure all components respect theme colors (some hardcoded colors may need updating)
- Test dropdown menu, admin panel, and all pages in dark mode before shipping
