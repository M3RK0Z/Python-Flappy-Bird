import pygame
import random
from game_object import GameObject

class Pipes:
    def __init__(self, width, gap, speed):
        self.width = width
        self.gap = gap
        self.speed = speed
        self.pipes = []
        self.spawn_pipe_event = pygame.USEREVENT + 1
        pygame.time.set_timer(self.spawn_pipe_event, 1500)

    def add_pipe(self, screen_height):
        random_pos = random.randint(200, 400)
        bottom_pipe = GameObject(
            pygame.display.get_surface().get_width(),
            random_pos,
            self.width,
            screen_height - random_pos,
            image_path="pipe_bottom.png"
        )
        top_pipe = GameObject(
            pygame.display.get_surface().get_width(),
            0,
            self.width,
            random_pos - self.gap,
            image_path="pipe_top.png"
        )
        self.pipes.extend([bottom_pipe, top_pipe])

    def update(self):
        self.pipes = [pipe for pipe in self.pipes if pipe.x > -self.width]
        for pipe in self.pipes:
            pipe.x -= self.speed

    def draw(self, screen):
        for pipe in self.pipes:
            pipe.draw(screen)

    def check_collision(self, bird_rect):
        return any(pipe.colliderect(bird_rect) for pipe in self.pipes)

    def update_score(self, bird_x, score):
        passed_pipes = filter(
            lambda pipe: pipe.x + self.width == bird_x,
            self.pipes
        )
        return score + 0.5 * len(list(passed_pipes))

    def reset(self):
        self.pipes.clear()