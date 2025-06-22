from game import FlappyBirdGame
import pygame

if __name__ == "__main__":
    pygame.init()  # Inicjalizacja pygame
    game = FlappyBirdGame()  # Utworzenie instancji gry
    game.run()  # Uruchomienie głównej pętli gry