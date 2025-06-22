import timeit
import cProfile
import pstats
import json
import random
import string
from collections import defaultdict
from datetime import datetime
from unittest.mock import MagicMock, patch

# Mockowanie pygame do testów wydajnościowych
pygame_mock = MagicMock()
pygame_mock.display.set_mode.return_value = MagicMock()
pygame_mock.font.SysFont.return_value = MagicMock()
pygame_mock.USEREVENT = 1
pygame_mock.time.get_ticks.return_value = 1000

class MockRect:
    """Mockowana klasa Rect do testów."""
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def colliderect(self, other):
        return False

pygame_mock.Rect = MockRect

with patch.dict('sys.modules', {'pygame': pygame_mock}):
    from game import FlappyBirdGame
    from bird import Bird
    from pipes import Pipes
    from utils import load_config, load_scores, save_score, get_player_scores

class PerformanceTests:
    """Klasa testów wydajnościowych."""
    def __init__(self):
        self.config = load_config()
        self.test_iterations = 1000  # Liczba iteracji dla każdego testu
        self.results = defaultdict(dict)  # Wyniki testów
        self.test_prefix = "PERF_TEST_"  # Prefix dla nazw testowych
        self.generated_names = set()  # Zbiór wygenerowanych nazw testowych

    def generate_test_name(self):
        """Generuje unikalną nazwę testową."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase, k=4))
        test_name = f"{self.test_prefix}{timestamp}_{random_str}"
        self.generated_names.add(test_name)
        return test_name

    def cleanup_test_data(self):
        """Automatycznie czyści wszystkie dane testowe."""
        if not self.generated_names:
            return

        try:
            scores = load_scores()
            if not scores or 'players' not in scores:
                return

            # Usuwa rekordy testowe
            initial_count = len(scores['players'])
            scores['players'] = [p for p in scores['players']
                                 if p['name'] not in self.generated_names]

            removed = initial_count - len(scores['players'])
            if removed > 0:
                with open('scores.json', 'w') as f:
                    json.dump(scores, f)
                print(f"\nCleaned up {removed} test records")
        except Exception as e:
            print(f"\nCleanup error: {str(e)}")

    def mock_user_input(self):
        """Mockuje wprowadzanie nazwy gracza."""
        FlappyBirdGame.show_name_input = lambda self: setattr(self, 'player_name', 'TEST_PLAYER')

    def test_game_initialization(self):
        """Testuje wydajność inicjalizacji gry."""
        self.mock_user_input()

        def init_game():
            game = FlappyBirdGame()
            return game

        time = timeit.timeit(init_game, number=self.test_iterations)
        self.results['Initialization']['Time'] = f"{time:.4f}s for {self.test_iterations} runs"
        self.results['Initialization']['Per_run'] = f"{(time / self.test_iterations) * 1000:.2f}ms"

    def test_bird_physics(self):
        """Testuje wydajność fizyki ptaka."""
        bird = Bird(100, 300, 30, self.config['gravity'], self.config['jump_force'])

        jump_time = timeit.timeit(bird.jump, number=self.test_iterations)
        update_time = timeit.timeit(bird.update, number=self.test_iterations)

        self.results['Bird Physics']['Jump'] = f"{jump_time:.4f}s for {self.test_iterations} jumps"
        self.results['Bird Physics']['Update'] = f"{update_time:.4f}s for {self.test_iterations} updates"

    def test_pipes_performance(self):
        """Testuje wydajność rur."""
        pipes = Pipes(self.config['pipe_width'], self.config['pipe_gap'], self.config['pipe_speed'])
        pipes.pipes = [
            MockRect(400, 300, self.config['pipe_width'], self.config['height'] - 300),
            MockRect(400, 0, self.config['pipe_width'], 150)
        ]

        update_time = timeit.timeit(pipes.update, number=self.test_iterations)
        collision_time = timeit.timeit(lambda: pipes.check_collision(MockRect(100, 300, 30, 30)),
                                       number=self.test_iterations)

        self.results['Pipes']['Update'] = f"{update_time:.4f}s for {self.test_iterations} updates"
        self.results['Pipes']['Collision_check'] = f"{collision_time:.4f}s for {self.test_iterations} checks"

    def test_score_operations(self):
        """Testuje wydajność operacji na wynikach."""
        test_name = self.generate_test_name()
        test_score = random.randint(1, 100)

        save_time = timeit.timeit(lambda: save_score(test_name, test_score), number=100)
        load_time = timeit.timeit(load_scores, number=self.test_iterations)
        search_time = timeit.timeit(lambda: get_player_scores(test_name), number=100)

        self.results['Score Operations']['Save'] = f"{save_time:.4f}s for 100 saves"
        self.results['Score Operations']['Load'] = f"{load_time:.4f}s for {self.test_iterations} loads"
        self.results['Score Operations']['Search'] = f"{search_time:.4f}s for 100 searches"

    def run_all_tests(self):
        """Uruchamia wszystkie testy wydajnościowe."""
        print("=== Running Performance Tests ===")
        print(f"Test prefix: {self.test_prefix}")

        try:
            self.test_game_initialization()
            self.test_bird_physics()
            self.test_pipes_performance()
            self.test_score_operations()

            print("\n=== Performance Results ===")
            for category, tests in self.results.items():
                print(f"\n{category}:")
                for test, result in tests.items():
                    print(f"  {test}: {result}")
        finally:
            self.cleanup_test_data()

if __name__ == '__main__':
    tester = PerformanceTests()
    tester.run_all_tests()