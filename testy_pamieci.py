from memory_profiler import profile
import json
import random
import string
from collections import defaultdict
from datetime import datetime
from unittest.mock import MagicMock, patch, PropertyMock
import gc

# Mockowanie pygame na potrzeby testów pamięci
pygame_mock = MagicMock()
pygame_mock.display.set_mode.return_value = MagicMock()
pygame_mock.font.SysFont.return_value = MagicMock()
pygame_mock.USEREVENT = 1
pygame_mock.time.get_ticks.return_value = 1000


# Klasa prostokąta do symulowania kolizji
class MockRect:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def colliderect(self, other):
        return False


pygame_mock.Rect = MockRect

# Załaduj moduły gry z podmienionym pygame
with patch.dict('sys.modules', {'pygame': pygame_mock}):
    from game import FlappyBirdGame
    from bird import Bird
    from pipes import Pipes
    from utils import load_config, load_scores, save_score, get_player_scores


class MemoryTests:
    """Klasa testów profilujących użycie pamięci"""

    def __init__(self):
        self.config = load_config()
        self.test_iterations = 100  # Liczba iteracji zmniejszona dla profilowania pamięci
        self.results = defaultdict(dict)
        self.test_prefix = "MEM_TEST_"
        self.generated_names = set()

    def generate_test_name(self):
        """Wygeneruj unikalną nazwę gracza do testu"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        random_str = ''.join(random.choices(string.ascii_uppercase, k=4))
        test_name = f"{self.test_prefix}{timestamp}_{random_str}"
        self.generated_names.add(test_name)
        return test_name

    def cleanup_test_data(self):
        """Usuń dane testowe z pliku scores.json po zakończeniu testów"""
        try:
            scores = load_scores()
            if scores and 'players' in scores:
                initial_count = len(scores['players'])
                scores['players'] = [p for p in scores['players']
                                     if p['name'] not in self.generated_names]

                if initial_count != len(scores['players']):
                    with open('scores.json', 'w') as f:
                        json.dump(scores, f)
                    print(f"\nUsunięto {initial_count - len(scores['players'])} rekordów testowych")
        except Exception as e:
            print(f"\nBłąd podczas czyszczenia danych: {str(e)}")

    def mock_user_input(self):
        """Zamockuj wejście użytkownika – ustaw stałą nazwę gracza"""
        FlappyBirdGame.show_name_input = lambda self: setattr(self, 'player_name', 'TEST_PLAYER')

    @profile(precision=4, stream=open('memory_game_init.log', 'w'))
    def test_game_initialization_memory(self):
        """Profilowanie pamięci przy inicjalizacji gry"""
        self.mock_user_input()
        games = []
        for _ in range(self.test_iterations):
            game = FlappyBirdGame()
            games.append(game)
        del games
        gc.collect()

    @profile(precision=4, stream=open('memory_bird_physics.log', 'w'))
    def test_bird_physics_memory(self):
        """Profilowanie pamięci dla fizyki ptaka"""
        birds = []
        for _ in range(self.test_iterations):
            bird = Bird(100, 300, 30, self.config['gravity'], self.config['jump_force'])
            bird.jump()
            bird.update()
            birds.append(bird)
        del birds
        gc.collect()

    @profile(precision=4, stream=open('memory_pipes.log', 'w'))
    def test_pipes_memory(self):
        """Profilowanie pamięci dla rur"""
        pipes_list = []
        for _ in range(self.test_iterations):
            pipes = Pipes(self.config['pipe_width'], self.config['pipe_gap'], self.config['pipe_speed'])

            # Dodaj rzeczywiste rury zamiast mocków
            for _ in range(5):
                pipe_mock = MagicMock()
                type(pipe_mock).x = PropertyMock(return_value=random.randint(0, 400))
                pipe_mock.width = self.config['pipe_width']
                pipes.pipes.append(pipe_mock)

            pipes.update()
            pipes.check_collision(MockRect(100, 300, 30, 30))
            pipes_list.append(pipes)
        del pipes_list
        gc.collect()

    @profile(precision=4, stream=open('memory_scores.log', 'w'))
    def test_score_operations_memory(self):
        """Profilowanie pamięci dla operacji na wynikach"""
        test_name = self.generate_test_name()
        test_score = random.randint(1, 100)

        # Zapisz wyniki testowe
        for _ in range(50):
            save_score(test_name, test_score)

        # Załaduj i przeszukaj dane
        scores_data = []
        for _ in range(self.test_iterations):
            scores_data.append(load_scores())
            get_player_scores(test_name)

        del scores_data
        gc.collect()

    def run_all_tests(self):
        """Uruchom wszystkie testy pamięci"""
        print("=== Uruchamianie testów profilowania pamięci ===")
        print(f"Prefiks testu: {self.test_prefix}")
        print("Wyniki zostaną zapisane do plików memory_*.log\n")

        try:
            print("Test: Inicjalizacja gry...")
            self.test_game_initialization_memory()

            print("Test: Fizyka ptaka...")
            self.test_bird_physics_memory()

            print("Test: Obsługa rur...")
            self.test_pipes_memory()

            print("Test: Operacje na wynikach...")
            self.test_score_operations_memory()

            print("\n=== Profilowanie pamięci zakończone ===")
            print("Sprawdź wygenerowane pliki logów:")
            print("- memory_game_init.log")
            print("- memory_bird_physics.log")
            print("- memory_pipes.log")
            print("- memory_scores.log")
        finally:
            self.cleanup_test_data()


if __name__ == '__main__':
    tester = MemoryTests()
    tester.run_all_tests()