import json
import os
import time
from functools import reduce
import matplotlib.pyplot as plt  # Dodane dla wykresów

# Dekorator do pomiaru czasu wykonania funkcji
def measure_time(func):
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        print(f"{func.__name__} wykonano w {time.time() - start:.4f}s")
        return result
    return wrapper

@measure_time
def load_config(filename='config.json'):
    """Wczytuje konfigurację gry z pliku JSON. Jeśli plik nie istnieje, używa domyślnych wartości."""
    default_config = {
        'width': 400,
        'height': 600,
        'bg_color': [0, 0, 139],
        'gravity': 0.25,
        'jump_force': 7,
        'pipe_width': 60,
        'pipe_gap': 150,
        'pipe_speed': 3,
        'fps': 60
    }

    try:
        with open(filename, 'r') as f:
            config = json.load(f)
            if 'bg_color' in config:
                config['bg_color'] = tuple(config['bg_color'])  # Konwersja listy na tuple dla koloru
            return {**default_config, **config}  # Łączenie domyślnych i wczytanych wartości
    except (FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Błąd wczytywania konfiguracji: {e}. Używam domyślnych wartości.")
        return default_config

def save_config(config, filename='config.json'):
    """Zapisuje konfigurację gry do pliku JSON."""
    try:
        with open(filename, 'w') as f:
            json.dump(config, f, indent=4)
        return True
    except IOError as e:
        print(f"Błąd zapisywania konfiguracji: {e}")
        return False

@measure_time
def save_score(name, score, filename='scores.json'):
    """Zapisuje wynik gracza do pliku JSON."""
    try:
        try:
            with open(filename, 'r') as f:
                scores = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            scores = {"players": []}

        # Dodanie nowego wyniku
        scores["players"].append({"name": name, "score": score})
        # Aktualizacja rekordu
        scores["high_score"] = max(scores["players"], key=lambda x: x["score"])["score"]

        with open(filename, 'w') as f:
            json.dump(scores, f, indent=4)
    except IOError as e:
        print(f"Błąd zapisywania wyniku: {e}")

def load_scores(filename='scores.json'):
    """Wczytuje wyniki z pliku JSON."""
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"players": [], "high_score": 0}  # Domyślne wartości jeśli plik nie istnieje

def get_player_scores(name, filename='scores.json'):
    """Pobiera wyniki konkretnego gracza."""
    try:
        with open(filename, 'r') as f:
            scores = json.load(f)
            player_scores = [score for score in scores["players"] if name.lower() in score["name"].lower()]
            return sorted(player_scores, key=lambda x: x["score"], reverse=True)  # Sortowanie malejąco
    except (FileNotFoundError, json.JSONDecodeError):
        return []

def get_average_score(filename='scores.json'):
    """Oblicza średni wynik wszystkich graczy."""
    try:
        with open(filename, 'r') as f:
            scores = json.load(f)
            if not scores["players"]:
                return 0
            total = reduce(lambda acc, x: acc + x["score"], scores["players"], 0)
            return round(total / len(scores["players"]), 2)
    except (FileNotFoundError, json.JSONDecodeError):
        return 0


def plot_scores(filename='scores.json'):
    """Generuje wykres najlepszych wyników, wyświetla go i zapisuje do pliku."""
    try:
        scores = load_scores(filename)
        if not scores["players"]:
            print("Brak danych do wygenerowania wykresu.")
            return

        # Przygotowanie danych - tylko najlepszy wynik każdego gracza
        players = {}
        for player in scores["players"]:
            name = player["name"]
            score = player["score"]
            if name not in players or score > players[name]:
                players[name] = score

        # Sortowanie i wybór top 10
        sorted_players = sorted(players.items(), key=lambda x: x[1], reverse=True)[:10]
        names = [player[0] for player in sorted_players]
        scores = [player[1] for player in sorted_players]

        # Stwórz wykres
        plt.figure(figsize=(10, 6))
        bars = plt.bar(names, scores, color='skyblue')
        plt.title("Top 10 Graczy - Flappy Bird", fontweight='bold')
        plt.xlabel("Gracz", fontstyle='italic')
        plt.ylabel("Wynik", fontstyle='italic')
        plt.xticks(rotation=45, ha='right')

        # Dodaj wartości na słupkach
        for bar in bars:
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2., height,
                     f'{int(height)}',
                     ha='center', va='bottom')

        plt.tight_layout()

        # Zapisz wykres do pliku
        plt.savefig("top_scores.png", dpi=100)
        print("📊 Wykres zapisano jako 'top_scores.png'.")

        # Wyświetl wykres
        plt.show()

    except Exception as e:
        print(f"❌ Błąd podczas generowania wykresu: {e}")