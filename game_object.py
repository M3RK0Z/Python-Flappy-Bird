import pygame


class GameObject:
    def __init__(self, x, y, width, height, color=None, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.color = color
        self.image = None

        # Dodane dla obsługi obrazów
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                print(f"Nie można załadować obrazu: {e}")
                self.color = color or (255, 255, 255)  # Domyślny kolor jeśli obraz się nie załaduje

    @property
    def x(self):
        return self.rect.x

    @x.setter
    def x(self, value):
        self.rect.x = value

    @property
    def y(self):
        return self.rect.y

    @y.setter
    def y(self, value):
        self.rect.y = value

    def colliderect(self, rect):
        return self.rect.colliderect(rect)

    def update(self):
        pass

    def draw(self, screen):
        if self.image:  # Najpierw próbujemy narysować obraz
            screen.blit(self.image, self.rect)
        elif self.color:  # Jeśli nie ma obrazu, używamy koloru
            pygame.draw.rect(screen, self.color, self.rect)