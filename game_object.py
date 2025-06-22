import pygame

class GameObject:
    """Bazowa klasa dla wszystkich obiektów gry."""
    def __init__(self, x, y, width, height, color=None, image_path=None):
        self.rect = pygame.Rect(x, y, width, height)  # Prostokąt kolizyjny
        self.color = color  # Kolor obiektu
        self.image = None   # Obraz obiektu

        # Wczytanie obrazu jeśli podano ścieżkę
        if image_path:
            try:
                self.image = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (width, height))
            except pygame.error as e:
                print(f"Nie można załadować obrazu: {e}")
                self.color = color or (255, 255, 255)  # Domyślny kolor jeśli obraz się nie załaduje

    @property
    def x(self):
        """Właściwość x obiektu."""
        return self.rect.x

    @x.setter
    def x(self, value):
        """Setter dla właściwości x."""
        self.rect.x = value

    @property
    def y(self):
        """Właściwość y obiektu."""
        return self.rect.y

    @y.setter
    def y(self, value):
        """Setter dla właściwości y."""
        self.rect.y = value

    def colliderect(self, rect):
        """Sprawdza kolizję z innym prostokątem."""
        return self.rect.colliderect(rect)

    def update(self):
        """Aktualizuje stan obiektu (do nadpisania w klasach pochodnych)."""
        pass

    def draw(self, screen):
        """Rysuje obiekt na ekranie."""
        if self.image:  # Najpierw próbuje narysować obraz
            screen.blit(self.image, self.rect)
        elif self.color:  # Jeśli nie ma obrazu, używa koloru
            pygame.draw.rect(screen, self.color, self.rect)