import unittest
import json
from unittest.mock import patch, MagicMock
from game import FlappyBirdGame
from bird import Bird
from pipes import Pipes
from utils import load_config, save_score, load_scores, get_player_scores

class TestFlappyBird(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        """Inicjalizacja przed wszystkimi testami - mockowanie pygame"""
        # Kompleksowe mockowanie pygame
        cls.pygame_mock = MagicMock()
        cls.pygame_mock.display.set_mode.return_value = MagicMock()
        cls.pygame_mock.font.SysFont.return_value = MagicMock()
        cls.pygame_mock.USEREVENT = 1
        cls.pygame_mock.time.get_ticks.return_value = 1000

        # Mock dla obiektu Rect
        class MockRect:
            def __init__(self, x, y, width, height):
                self.x = x
                self.y = y
                self.width = width
                self.height = height

            def colliderect(self, other):
                return False

        cls.pygame_mock.Rect = MockRect

        # Mockowanie całego modułu pygame
        cls.patcher = patch.dict('sys.modules', {'pygame': cls.pygame_mock})
        cls.patcher.start()

        # Mockowanie metody show_name_input
        cls.original_show_name_input = FlappyBirdGame.show_name_input
        FlappyBirdGame.show_name_input = lambda self: setattr(self, 'player_name', 'TEST_PLAYER')

        cls.game = FlappyBirdGame()
        cls.config = load_config()

    @classmethod
    def tearDownClass(cls):
        """Sprzątanie po wszystkich testach"""
        # Przywracanie oryginalnej implementacji
        FlappyBirdGame.show_name_input = cls.original_show_name_input
        cls.patcher.stop()

    def setUp(self):
        """Inicjalizacja przed każdym testem"""
        self.test_name = f"TEST_{self.id()}"  # Unikalna nazwa testowa
        self.test_score = 10

    def tearDown(self):
        """Sprzątanie po każdym teście - usuwanie danych testowych"""
        scores = load_scores()
        if scores and 'players' in scores:
            scores['players'] = [p for p in scores['players'] if p['name'] != self.test_name]
            with open('scores.json', 'w') as f:
                json.dump(scores, f)

    def test_load_config(self):
        """Test wczytywania konfiguracji"""
        config = load_config()
        self.assertIsInstance(config, dict)
        self.assertIn('width', config)
        self.assertIn('height', config)
        self.assertIn('gravity', config)

    def test_save_and_load_scores(self):
        """Test zapisywania i wczytywania wyników"""
        save_score(self.test_name, self.test_score)
        scores = load_scores()
        self.assertIn("players", scores)
        self.assertTrue(any(player["name"] == self.test_name for player in scores["players"]))

    def test_get_player_scores(self):
        """Test pobierania wyników konkretnego gracza"""
        save_score(self.test_name, self.test_score)
        scores = get_player_scores(self.test_name)
        self.assertTrue(all(self.test_name.lower() in score["name"].lower() for score in scores))

    def test_bird_jump(self):
        """Test działania skoku ptaka"""
        bird = Bird(100, 300, 30, 0.25, 7)
        bird.jump()
        self.assertEqual(bird.movement, -7)  # Sprawdzenie czy ruch został ustawiony poprawnie

    def test_pipes_collision(self):
        """Test wykrywania kolizji z rurami"""
        pipes = Pipes(60, 150, 3)
        bird = Bird(100, 300, 30, 0.25, 7)
        pipes.add_pipe(600)
        # Symulacja kolizji
        bird.rect.x = pipes.pipes[0].x
        bird.rect.y = pipes.pipes[0].y
        self.assertTrue(pipes.check_collision(bird.rect))

    @patch('pygame.mixer.Sound')
    def test_bird_jump_sound(self, mock_sound):
        """Test odtwarzania dźwięku skoku"""
        bird = Bird(100, 300, 30, 0.25, 7)
        bird.jump()
        if bird.jump_sound:
            bird.jump_sound.play.assert_called_once()  # Sprawdzenie czy dźwięk został odtworzony

    def test_game_reset(self):
        """Test resetowania gry"""
        self.game.start_game()
        self.game.bird.rect.y = 0  # Symulacja uderzenia w sufit
        self.game.update()
        self.assertFalse(self.game.game_active)  # Czy gra została zatrzymana
        self.assertTrue(self.game.menu_active)    # Czy menu zostało aktywowane

    def test_game_initialization_integration(self):
        """Testuje poprawne inicjalizowanie wszystkich komponentów gry"""
        self.assertIsInstance(self.game.bird, Bird)
        self.assertIsInstance(self.game.pipes, Pipes)
        self.assertEqual(self.game.player_name, "TEST_PLAYER")
        self.assertEqual(self.game.config['width'], 400)
        self.assertEqual(self.game.config['height'], 650)
        self.assertFalse(self.game.game_active)
        self.assertTrue(self.game.menu_active)

if __name__ == '__main__':
    unittest.main()