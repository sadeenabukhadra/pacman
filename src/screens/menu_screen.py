from src.screens.base_screen import BaseScreen
from src.ui.button import Button
import pygame
class MenuScreen(BaseScreen):
    def __init__(self,surface:pygame.Surface) ->None:
        super().__init__(surface)
        self.selected_index:int = 0
        self.font:pygame.font.Font=pygame.font.Font(None,36)
        self.buttons:list[Button] = []
        buttons_texts=[
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
            x = self.surface.get_width() - button_width -100
            y = 250 + index *(button_height + button_gap)
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
        self.buttons[self.selected_index].set_selected(True)
            
    def handle_event(self, event: pygame.event.Event):
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_DOWN:
                self.selected_index = (
                    self.selected_index + 1
                ) % len(self.buttons)
            elif event.key == pygame.K_UP:
                self.selected_index = (
                    self.selected_index - 1
                ) % len(self.buttons)
            elif event.key == pygame.K_RETURN:
                self.activate_selected_button()
            for index, button in enumerate(self.buttons):
                button.set_selected(
                    index == self.selected_index
                )
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                for index, button in enumerate(self.buttons):
                    if button.is_hovered(event.post):
                        self.selected_index = index
                        self.update_selection()
                        self._activate_selected_button()
                        break



                    

