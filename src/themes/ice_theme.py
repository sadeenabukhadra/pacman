"""Ice world."""

from src.themes.theme import Theme

ICE_THEME = Theme(
    name="ice",
    floor="floor_ice",
    block="block",
    background="background",
    hud_panel="hud_panel",
    game_over_image="gameover_ice.png",
    fallback_color=(20, 40, 90),
    wall_color=(210, 245, 255),
    glow_color=(80, 170, 255),
)