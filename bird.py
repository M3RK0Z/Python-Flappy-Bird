import pygame
from game_object import GameObject

class Bird(GameObject):
    """Klasa reprezentująca ptaka w grze."""
    def __init__(self, x, y, size, gravity, jump_force):
        super().__init__(x, y, size, size, image_path="bird.png")
        self.gravity = gravity      # Wartość grawitacji
        self.jump_force = jump_force  # Siła skoku
        self.movement = 0           # Aktualna prędkość ruchu w pionie
        self.initial_y = y          # Początkowa pozycja Y (do resetu)

        # Inicjalizacja dźwięku skoku
        try:
            self.jump_sound = pygame.mixer.Sound("jump.wav")
            self.jump_sound.set_volume(0.1)  # Ustawienie głośności
        except pygame.error as e:
            print(f"Nie można załadować dźwięku skoku: {e}")
            self.jump_sound = None

    def jump(self):
        """Wykonuje skok ptaka."""
        self.movement = -self.jump_force  # Ujemna wartość bo Y rośnie w dół
        if self.jump_sound:
            self.jump_sound.play()  # Odtworzenie dźwięku

    def update(self):
        """Aktualizuje pozycję ptaka na podstawie grawitacji."""
        self.movement += self.gravity
        self.rect.y += self.movement

    def reset(self):
        """Resetuje pozycję i prędkość ptaka."""
        self.rect.y = self.initial_y
        self.movement = 0