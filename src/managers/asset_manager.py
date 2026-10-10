import pygame


class AssetManager:
    def __init__(self) -> None:
        self.images: dict[str, pygame.Surface] = {}
        self.fonts: dict[str, pygame.font.Font] = {}

    def load_image(
        self,
        name: str,
        path: str,
    ) -> pygame.Surface:
        image = pygame.image.load(path).convert_alpha()
        self.images[name] = image
        return image

    def get_image(self, name: str) -> pygame.Surface | None:
        return self.images.get(name)

    def load_font(
        self,
        name: str,
        path: str | None,
        size: int,
    ) -> pygame.font.Font:
        font = pygame.font.Font(path, size)
        self.fonts[name] = font
        return font

    def get_font(self, name: str) -> pygame.font.Font | None:
        return self.fonts.get(name)