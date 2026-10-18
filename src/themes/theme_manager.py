"""Keep track of the selected theme."""

from src.themes.cosmic_theme import COSMIC_THEME
from src.themes.ice_theme import ICE_THEME
from src.themes.theme import Theme

THEMES: dict[str, Theme] = {
    ICE_THEME.name: ICE_THEME,
    COSMIC_THEME.name: COSMIC_THEME,
}
DEFAULT_THEME = ICE_THEME.name


class ThemeManager:
    """Store the current theme and let the game change it."""

    def __init__(self, name: str = DEFAULT_THEME) -> None:
        """Select the first theme.

        Args:
            name: Theme name ("ice" or "cosmic").
        """
        self.current: Theme = THEMES[DEFAULT_THEME]
        self.set_theme(name)

    def set_theme(self, name: str) -> None:
        """Change the theme; an unknown name keeps the current one."""
        theme = THEMES.get(name)

        if theme is None:
            print(
                f"Warning: unknown theme '{name}'. Keeping "
                f"'{self.current.name}'."
            )
            return

        self.current = theme
