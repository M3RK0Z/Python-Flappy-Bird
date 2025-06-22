import pygame
import random
from game_object import GameObject


class Pipes:
    """Klasa reprezentująca rury (przeszkody) w grze."""

    def __init__(self, width, gap, speed):
        self.width = width  # Szerokość rury
        self.gap = gap  # Odstęp między górną i dolną rurą
        self.speed = speed  # Prędkość przesuwania się rur
        self.pipes = []  # Lista aktywnych rur

        # Zdarzenie timerowe do generowania nowych rur
        self.spawn_pipe_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.spawn_pipe_event, 1500)  # Nowa rura co 1500 ms

    def add_pipe(self, screen_height):
        """Dodaje nową parę rur (górną i dolną)."""
        random_pos = random.randint(200, 400)  # Losowa pozycja odstępu
        # Dolna rura
        bottom_pipe = GameObject(
            pygame.display.get_surface().get_width(),
            random_pos,
            self.width,
            screen_height - random_pos,
            image_path="pipe_bottom.png"
        )
        # Górna rura
        top_pipe = GameObject(
            pygame.display.get_surface().get_width(),
            0,
            self.width,
            random_pos - self.gap,
            image_path="pipe_top.png"
        )
        self.pipes.extend([bottom_pipe, top_pipe])

    def update(self):
        """Aktualizuje pozycje rur."""
        # Usuwa rury, które wyszły poza ekran
        self.pipes = [pipe for pipe in self.pipes if pipe.x > -self.width]
        # Przesuwa wszystkie rury
        for pipe in self.pipes:
            pipe.x -= self.speed

    def draw(self, screen):
        """Rysuje wszystkie rury na ekranie."""
        for pipe in self.pipes:
            pipe.draw(screen)

    def check_collision(self, bird_rect):
        """Sprawdza kolizję ptaka z jakąkolwiek rurą."""
        return any(pipe.colliderect(bird_rect) for pipe in self.pipes)

    def update_score(self, bird_x, score):
        """Aktualizuje wynik, gdy ptak minął parę rur."""
        passed_pipes = filter(
            lambda pipe: pipe.x + self.width == bird_x,
            self.pipes
        )
        return score + 0.5 * len(list(passed_pipes))  # 0.5 bo każda para to 2 rury

    def reset(self):
        """Resetuje stan rur."""
        self.pipes.clear()