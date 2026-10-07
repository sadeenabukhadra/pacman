import pygame

from src.managers.screen_manager import ScreenManager
from src.screens.base_screen import BaseScreen
from src.ui.button import Button


class MenuScreen(BaseScreen):
    def __init__(
        self,
        surface: pygame.Surface,
        screen_manager: ScreenManager,
    ) -> None:
        super().__init__(surface)

        self.screen_manager: ScreenManager = screen_manager

        self.selected_index: int = 0
        self.font: pygame.font.Font = pygame.font.Font(None, 36)
        self.buttons: list[Button] = []

        buttons_texts: list[str] = [
            "START GAME",
            "INSTRUCTIONS",
            "HIGH SCORES",
            "SETTINGS",
            "QUIT GAME",
        ]

        button_width: int = 300
        button_height: int = 60
        button_gap: int = 20

        for index, text in enumerate(buttons_texts):
            x = self.surface.get_width() - button_width - 100
            y = 250 + index * (button_height + button_gap)

            rect = pygame.Rect(
                x,
                y,
                button_width,
                button_height,
            )

            button = Button(
                rect=rect,
                text=text,
                font=self.font,
                normal_color=(30, 45, 70),
                selected_color=(70, 160, 220),
            )

            self.buttons.append(button)

        self._update_selection()

    def handle_event(self, event: pygame.event.Event) -> None:
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (
                    self.selected_index + 1
                ) % len(self.buttons)

                self._update_selection()

            elif event.key == pygame.K_UP:
                self.selected_index = (
                    self.selected_index - 1
                ) % len(self.buttons)

                self._update_selection()

            elif event.key == pygame.K_RETURN:
                self._activate_selected_button()

        elif event.type == pygame.MOUSEMOTION:
            for index, button in enumerate(self.buttons):
                if button.is_hovered(event.pos):
                    self.selected_index = index
                    self._update_selection()
                    break

        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, button in enumerate(self.buttons):
                    if button.is_hovered(event.pos):
                        self.selected_index = index
                        self._update_selection()
                        self._activate_selected_button()
                        break

    def _update_selection(self) -> None:
        for index, button in enumerate(self.buttons):
            button.set_selected(
                index == self.selected_index
            )

    def _activate_selected_button(self) -> None:
        if self.selected_index == 0:
            # START GAME
            pass

        elif self.selected_index == 1:
            # INSTRUCTIONS
            pass

        elif self.selected_index == 2:
            # HIGH SCORES
            pass

        elif self.selected_index == 3:
            # SETTINGS
            pass

        elif self.selected_index == 4:
            # QUIT GAME
            pygame.event.post(
                pygame.event.Event(pygame.QUIT)
            )

    def update(self, dt: float) -> None:
        pass

    def render(self) -> None:
        self.surface.fill((10, 20, 40))

        for button in self.buttons:
            button.render(self.surface)
