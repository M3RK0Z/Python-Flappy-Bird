import pygame
from game_object import GameObject

class Bird(GameObject):
    def __init__(self, x, y, size, gravity, jump_force):
        super().__init__(x, y, size, size, image_path="bird.png")
        self.gravity = gravity
        self.jump_force = jump_force
        self.movement = 0
        self.initial_y = y

        # Dodajemy dźwięk skoku
        try:
            self.jump_sound = pygame.mixer.Sound("jump.wav")
            self.jump_sound.set_volume(0.1)  # Możesz dostosować głośność (0.0 - 1.0)
        except pygame.error as e:
            print(f"Nie można załadować dźwięku skoku: {e}")
            self.jump_sound = None

    def jump(self):
        self.movement = -self.jump_force
        # Odtwarzamy dźwięk przy skoku
        if self.jump_sound:
            self.jump_sound.play()

    def update(self):
        self.movement += self.gravity
        self.rect.y += self.movement

    def reset(self):
        self.rect.y = self.initial_y
        self.movement = 0