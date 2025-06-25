import unittest
from unittest.mock import patch, MagicMock, PropertyMock
from game import FlappyBirdGame


class QuickFlappyBirdTest(unittest.TestCase):
    def setUp(self):
        # Kompleksowe mockowanie pygame
        self.pygame_patcher = patch('pygame.display')
        self.pygame_mixer_patcher = patch('pygame.mixer')
        self.pygame_draw_patcher = patch('pygame.draw')
        self.pygame_font_patcher = patch('pygame.font')

        # Mockowanie modułów pygame
        self.mock_display = self.pygame_patcher.start()
        self.mock_mixer = self.pygame_mixer_patcher.start()
        self.mock_draw = self.pygame_draw_patcher.start()
        self.mock_font = self.pygame_font_patcher.start()

        # Mockowanie powierzchni ekranu
        self.mock_screen = MagicMock()
        self.mock_display.set_mode.return_value = self.mock_screen
        self.mock_display.get_surface.return_value = self.mock_screen

        # Poprawne mockowanie metod get_width() i get_height()
        self.mock_screen.get_width = MagicMock(return_value=400)
        self.mock_screen.get_height = MagicMock(return_value=600)

        # Mockowanie czcionki
        self.mock_font.SysFont.return_value.render.return_value = MagicMock(
            get_rect=lambda: MagicMock(width=100, height=20)
        )

        # Mockowanie zdarzeń pygame
        self.pygame = MagicMock()
        self.pygame.USEREVENT = 1
        self.pygame.K_SPACE = 32
        self.pygame.QUIT = 256
        self.pygame.Rect = lambda x, y, w, h: MagicMock(x=x, y=y, width=w, height=h)

        # Globalne mockowanie pygame
        self.pygame_global_patcher = patch.dict('sys.modules', {'pygame': self.pygame})
        self.pygame_global_patcher.start()

    def tearDown(self):
        self.pygame_patcher.stop()
        self.pygame_mixer_patcher.stop()
        self.pygame_draw_patcher.stop()
        self.pygame_font_patcher.stop()
        self.pygame_global_patcher.stop()

    def test_essential_game_mechanics(self):
        # Pomijamy ekran wprowadzania nazwy
        with patch.object(FlappyBirdGame, 'show_name_input', lambda self: setattr(self, 'player_name', 'TEST')):
            game = FlappyBirdGame()
            game.start_game()

        # Test skoku ptaka
        initial_y = game.bird.rect.y
        game.bird.jump()
        game.bird.update()
        self.assertLess(game.bird.rect.y, initial_y)

        # Symulacja kolizji
        game.pipes.add_pipe(game.config['height'])
        game.bird.rect.x = game.pipes.pipes[0].x
        game.bird.rect.y = game.pipes.pipes[0].y
        game.update()

        # Weryfikacja końca gry
        self.assertFalse(game.game_active)
        self.assertEqual(game.score, 0)


if __name__ == '__main__':
    unittest.main()