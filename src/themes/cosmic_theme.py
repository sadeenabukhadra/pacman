"""Cosmic world."""

from src.themes.theme import Theme

COSMIC_THEME = Theme(
    name="cosmic",
    floor="floor_space",
    block="block",
    background="background",
    hud_panel="hud_panel",
    game_over_image="gameover_cosmic.png",
    fallback_color=(25, 10, 60),
    wall_color=(140, 235, 255),
    glow_color=(210, 70, 255),
)