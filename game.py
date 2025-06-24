import pygame
import json
from bird import Bird
from pipes import Pipes
from utils import load_config, save_score, load_scores, get_player_scores


class FlappyBirdGame:
    def __init__(self):
        # Kolory używane w grze
        self.orange_color = (255, 165, 0)
        self.dark_orange = (200, 120, 0)
        self.white = (255, 255, 255)
        self.black = (0, 0, 0)

        # Wczytanie konfiguracji i wyników
        self.config = load_config()
        self.scores_data = load_scores()
        self.player_name = ""
        self.setup_game()
        self.check_first_run()

        # Flagi stanów gry
        self.menu_active = True
        self.options_active = False
        self.scores_active = False

        # Indeksy wybranych opcji w menu
        self.selected_menu_item = 0
        self.selected_option = 0
        self.menu_items = ["Start", "Opcje", "Wyniki", "Wyjdź"]

        # Zmienne związane z wyszukiwaniem wyników
        self.search_mode = "all"
        self.search_term = ""
        self.search_active = False

        # Inicjalizacja muzyki
        self.music_playing = False
        self.init_music()

    def setup_game(self):
        """Inicjalizacja podstawowych elementów gry."""
        pygame.init()
        pygame.mixer.init()
        self.screen = pygame.display.set_mode(
            (self.config['width'], self.config['height'])
        )
        pygame.display.set_caption("Flappy Bird - Projekt Python")

        # Wczytanie tła
        try:
            self.background = pygame.image.load("tlo.png").convert()
            self.background = pygame.transform.scale(self.background, (self.config['width'], self.config['height']))
        except pygame.error:
            self.background = None

        # Inicjalizacja zegara i czcionek
        self.clock = pygame.time.Clock()
        self.font_large = pygame.font.SysFont('Arial', 50, bold=True)
        self.font_medium = pygame.font.SysFont('Arial', 30, bold=True)
        self.font_small = pygame.font.SysFont('Arial', 20)

        # Inicjalizacja ptaka i rur
        self.bird = Bird(
            x=100,
            y=self.config['height'] // 2,
            size=30,
            gravity=self.config['gravity'],
            jump_force=self.config['jump_force']
        )

        self.pipes = Pipes(
            width=self.config['pipe_width'],
            gap=self.config['pipe_gap'],
            speed=self.config['pipe_speed']
        )

        # Inicjalizacja wyników
        self.score = 0
        self.high_score = self.scores_data.get('high_score', 0)
        self.game_active = False

    def init_music(self):
        """Inicjalizacja muzyki w tle."""
        try:
            pygame.mixer.music.load("background_music.mp3")
            pygame.mixer.music.set_volume(0.1)
            pygame.mixer.music.play(-1)  # -1 oznacza zapętlanie
            self.music_playing = True
        except pygame.error as e:
            print(f"Nie można załadować muzyki: {e}")
            self.music_playing = False

    def check_first_run(self):
        """Sprawdza, czy gra jest uruchamiana po raz pierwszy i prosi o podanie nazwy gracza."""
        if not hasattr(self, 'player_name') or not self.player_name:
            self.show_name_input()

    def show_name_input(self):
        """Wyświetla ekran wprowadzania nazwy gracza."""
        input_active = True
        name = ""
        font_title = pygame.font.SysFont('Arial', 36, bold=True)
        font_input = pygame.font.SysFont('Arial', 24)
        font_prompt = pygame.font.SysFont('Arial', 18)

        while input_active:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN and name:
                        self.player_name = name
                        input_active = False
                    elif event.key == pygame.K_BACKSPACE:
                        name = name[:-1]
                    else:
                        name += event.unicode

            # Rysowanie interfejsu wprowadzania nazwy
            self.screen.fill(self.config['bg_color'])
            title = font_title.render("Wprowadź swoją nazwę", True, self.white)
            self.screen.blit(title, (self.config['width'] // 2 - title.get_width() // 2, 100))

            # Pole wprowadzania tekstu
            name_text = font_input.render(name, True, self.white)
            pygame.draw.rect(self.screen, self.white,
                             (self.config['width'] // 2 - 150, 180, 300, 40), 2, border_radius=10)
            self.screen.blit(name_text, (self.config['width'] // 2 - name_text.get_width() // 2, 190))

            # Podpowiedź
            prompt = font_prompt.render("Naciśnij Enter aby kontynuować", True, self.white)
            self.screen.blit(prompt, (self.config['width'] // 2 - prompt.get_width() // 2, 250))

            pygame.display.flip()
            self.clock.tick(self.config['fps'])

    def draw_button(self, x, y, width, height, text, is_selected=False, is_hovered=False):
        """Rysuje przycisk na ekranie."""
        button_color = self.dark_orange if is_selected or is_hovered else self.orange_color
        pygame.draw.rect(self.screen, button_color, (x, y, width, height), border_radius=15)
        pygame.draw.rect(self.screen, self.black, (x, y, width, height), 2, border_radius=15)

        text_surface = self.font_medium.render(text, True, self.black)
        text_rect = text_surface.get_rect(center=(x + width // 2, y + height // 2))
        self.screen.blit(text_surface, text_rect)
        return pygame.Rect(x, y, width, height)

    def handle_events(self):
        """Obsługuje zdarzenia w grze."""
        running = True
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

            if event.type == self.pipes.spawn_pipe_event and self.game_active:
                self.pipes.add_pipe(self.config['height'])

            if event.type == pygame.KEYDOWN:
                if self.menu_active and not self.options_active and not self.scores_active:
                    if event.key == pygame.K_DOWN:
                        self.selected_menu_item = (self.selected_menu_item + 1) % len(self.menu_items)
                    elif event.key == pygame.K_UP:
                        self.selected_menu_item = (self.selected_menu_item - 1) % len(self.menu_items)
                    elif event.key == pygame.K_RETURN:
                        self.handle_menu_selection()
                elif self.options_active:
                    if event.key == pygame.K_DOWN:
                        self.selected_option = (self.selected_option + 1) % 6
                    elif event.key == pygame.K_UP:
                        self.selected_option = (self.selected_option - 1) % 6
                    elif event.key == pygame.K_RETURN:
                        self.handle_options_selection()
                    elif event.key == pygame.K_ESCAPE:
                        self.options_active = False
                elif self.scores_active:
                    if event.key == pygame.K_ESCAPE:
                        self.scores_active = False
                    elif self.search_active:
                        if event.key == pygame.K_RETURN:
                            self.search_active = False
                        elif event.key == pygame.K_BACKSPACE:
                            self.search_term = self.search_term[:-1]
                        elif event.key == pygame.K_ESCAPE:
                            self.search_active = False
                            self.search_term = ""
                        else:
                            self.search_term += event.unicode
                elif event.key == pygame.K_SPACE and self.game_active:
                    self.bird.jump()
                elif event.key == pygame.K_ESCAPE and self.game_active:
                    self.game_active = False
                    self.menu_active = True

            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()

                if self.game_active:
                    self.bird.jump()
                elif self.menu_active and not self.options_active and not self.scores_active:
                    self.check_menu_click(mouse_pos)
                elif self.options_active:
                    self.check_options_click(mouse_pos)
                elif self.scores_active:
                    self.handle_scores_click(mouse_pos)

        return running

    def handle_menu_selection(self):
        """Obsługuje wybór opcji w menu głównym."""
        if self.selected_menu_item == 0:  # Start
            self.start_game()
        elif self.selected_menu_item == 1:  # Opcje
            self.options_active = True
            self.selected_option = 0
        elif self.selected_menu_item == 2:  # Wyniki
            self.scores_active = True
        elif self.selected_menu_item == 3:  # Wyjdź
            pygame.quit()
            exit()

    def handle_options_selection(self):
        """Obsługuje wybór opcji w menu opcji."""
        if self.selected_option == 4:  # Zmień nazwę
            self.show_name_input()
        elif self.selected_option == 5:  # Powrót
            self.options_active = False

    def check_menu_click(self, mouse_pos):
        """Sprawdza kliknięcie w przyciski menu głównego."""
        button_width = 200
        button_height = 50
        start_y = 200

        for i, item in enumerate(self.menu_items):
            button_rect = pygame.Rect(
                self.config['width'] // 2 - button_width // 2,
                start_y + i * (button_height + 20),
                button_width,
                button_height
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_menu_item = i
                self.handle_menu_selection()
                break

    def check_options_click(self, mouse_pos):
        """Sprawdza kliknięcie w przyciski menu opcji."""
        button_width = 300
        button_height = 40
        start_y = 150

        for i in range(6):  # 6 opcji w menu opcji
            button_rect = pygame.Rect(
                self.config['width'] // 2 - button_width // 2,
                start_y + i * (button_height + 10),
                button_width,
                button_height
            )
            if button_rect.collidepoint(mouse_pos):
                self.selected_option = i
                self.handle_options_selection()
                break

    def handle_scores_click(self, mouse_pos):
        """Obsługuje kliknięcia w ekranie wyników."""
        plot_button_rect, back_button_rect = self.render_high_scores()

        # Sprawdź kliknięcie w pole wyszukiwania
        search_rect = pygame.Rect(self.config['width'] // 2 - 150, 120, 300, 30)
        if search_rect.collidepoint(mouse_pos):
            self.search_active = True
            self.search_term = ""

        # Sprawdź kliknięcie przycisku "Wszyscy"
        all_rect = pygame.Rect(self.config['width'] // 2 - 200, 160, 100, 30)
        if all_rect.collidepoint(mouse_pos):
            self.search_mode = "all"
            self.search_active = False

        # Sprawdź kliknięcie przycisku "Szukaj"
        search_btn_rect = pygame.Rect(self.config['width'] // 2 + 100, 160, 100, 30)
        if search_btn_rect.collidepoint(mouse_pos):
            self.search_mode = "search"
            self.search_active = False

        # Sprawdź kliknięcie przycisku "Generuj wykres"
        if plot_button_rect.collidepoint(mouse_pos):
            from utils import plot_scores
            plot_scores()
            self.scores_data = load_scores()
            pygame.time.delay(300)

        # Sprawdź kliknięcie przycisku "Powrót"
        if back_button_rect.collidepoint(mouse_pos):
            self.scores_active = False

    def start_game(self):
        """Rozpoczyna nową grę."""
        self.menu_active = False
        self.game_active = True
        self.reset_game()

    def update(self):
        """Aktualizuje stan gry."""
        if self.game_active:
            self.bird.update()
            self.pipes.update()

            # Sprawdzenie kolizji
            if self.pipes.check_collision(self.bird.rect) or \
                    self.bird.rect.top <= 0 or \
                    self.bird.rect.bottom >= self.config['height']:
                self.game_over()

            self.score = self.pipes.update_score(self.bird.rect.x, self.score)

    def render(self):
        """Renderuje grę na ekranie."""
        # Rysowanie tła
        if self.background:
            self.screen.blit(self.background, (0, 0))
        else:
            self.screen.fill(self.config['bg_color'])

        if self.scores_active:
            self.render_high_scores()
        elif self.menu_active:
            if self.options_active:
                self.render_options()
            else:
                self.render_menu()
        elif self.game_active:
            self.pipes.draw(self.screen)
            self.bird.draw(self.screen)
            score_text = self.font_medium.render(f"Wynik: {int(self.score)}", True, self.white)
            self.screen.blit(score_text, (20, 20))
            name_text = self.font_small.render(f"Gracz: {self.player_name}", True, self.white)
            self.screen.blit(name_text, (20, 50))

        pygame.display.update()

    def render_menu(self):
        """Renderuje menu główne."""
        title = self.font_large.render("Flappy Bird", True, self.white)
        self.screen.blit(title, (self.config['width'] // 2 - title.get_width() // 2, 100))

        mouse_pos = pygame.mouse.get_pos()
        button_width = 200
        button_height = 50
        start_y = 200

        # Renderowanie przycisków menu
        for i, item in enumerate(self.menu_items):
            button_rect = self.draw_button(
                self.config['width'] // 2 - button_width // 2,
                start_y + i * (button_height + 20),
                button_width,
                button_height,
                item,
                i == self.selected_menu_item,
                self.is_button_hovered(mouse_pos, self.config['width'] // 2 - button_width // 2,
                                       start_y + i * (button_height + 20),
                                       button_width, button_height)
            )

        # Wyświetlanie rekordu i nazwy gracza
        high_score = self.font_small.render(f"Rekord: {int(self.high_score)}", True, self.white)
        self.screen.blit(high_score,
                         (self.config['width'] // 2 - high_score.get_width() // 2, 480))

        player_text = self.font_small.render(f"Gracz: {self.player_name}", True, self.white)
        self.screen.blit(player_text,
                         (self.config['width'] // 2 - player_text.get_width() // 2, 510))

    def is_button_hovered(self, mouse_pos, x, y, width, height):
        """Sprawdza, czy kursor myszy znajduje się nad przyciskiem."""
        button_rect = pygame.Rect(x, y, width, height)
        return button_rect.collidepoint(mouse_pos)

    def render_options(self):
        """Renderuje menu opcji."""
        title = self.font_large.render("Opcje", True, self.white)
        self.screen.blit(title, (self.config['width'] // 2 - title.get_width() // 2, 50))

        options = [
            f"Rozdzielczość: {self.config['width']}x{self.config['height']}",
            f"Grawitacja: {self.config['gravity']}",
            f"Siła skoku: {self.config['jump_force']}",
            f"Twoja nazwa: {self.player_name}",
            "Zmień nazwę",
            "Powrót"
        ]

        mouse_pos = pygame.mouse.get_pos()
        button_width = 300
        button_height = 40
        start_y = 150

        for i, option in enumerate(options):
            button_rect = self.draw_button(
                self.config['width'] // 2 - button_width // 2,
                start_y + i * (button_height + 10),
                button_width,
                button_height,
                option,
                i == self.selected_option,
                self.is_button_hovered(mouse_pos, self.config['width'] // 2 - button_width // 2,
                                       start_y + i * (button_height + 10),
                                       button_width, button_height)
            )

    def render_high_scores(self):
        """Renderuje ekran z najlepszymi wynikami."""
        self.screen.fill(self.config['bg_color'])
        title = self.font_large.render("Najlepsze wyniki", True, self.white)
        self.screen.blit(title, (self.config['width'] // 2 - title.get_width() // 2, 50))

        # Pole wyszukiwania
        search_rect = pygame.Rect(self.config['width'] // 2 - 150, 120, 300, 30)
        pygame.draw.rect(self.screen, (50, 50, 100), search_rect, border_radius=5)

        if self.search_active:
            search_text = self.search_term
            cursor = "|" if pygame.time.get_ticks() % 1000 < 500 else ""
            search_surface = self.font_small.render(search_text + cursor, True, self.white)
        else:
            search_text = "Wyszukaj gracza..." if not self.search_term else self.search_term
            search_surface = self.font_small.render(search_text, True, self.white)
        self.screen.blit(search_surface, (self.config['width'] // 2 - 140, 125))

        # Przyciski filtrowania
        mouse_pos = pygame.mouse.get_pos()
        all_button = self.draw_button(
            self.config['width'] // 2 - 200, 160, 100, 30, "Wszyscy",
            self.search_mode == "all", False
        )
        search_button = self.draw_button(
            self.config['width'] // 2 + 100, 160, 100, 30, "Szukaj",
            self.search_mode == "search", False
        )

        # Tło dla wyników
        results_bg_rect = pygame.Rect(
            self.config['width'] // 2 - 150, 200, 300, 320
        )
        pygame.draw.rect(self.screen, (50, 50, 100), results_bg_rect, border_radius=15)

        # Pobierz i wyświetl wyniki
        if self.search_mode == "all":
            scores_to_show = sorted(self.scores_data["players"], key=lambda x: x["score"], reverse=True)[:10]
        else:
            scores_to_show = get_player_scores(self.search_term if self.search_term else " ")

        score_texts = list(map(
            lambda s: f"{s['name']}: {int(s['score'])}",
            scores_to_show[:10]
        )) if scores_to_show else ["Brak wyników"]

        for i, text in enumerate(score_texts):
            rendered_text = self.font_medium.render(text, True, self.white)
            self.screen.blit(rendered_text,
                             (self.config['width'] // 2 - rendered_text.get_width() // 2,
                              210 + i * 30))

        # Przycisk generowania wykresu
        plot_button_rect = pygame.Rect(
            self.config['width'] // 2 - 100, self.config['height'] - 120, 200, 50
        )
        is_hovered = plot_button_rect.collidepoint(mouse_pos)
        self.draw_button(
            plot_button_rect.x, plot_button_rect.y,
            plot_button_rect.width, plot_button_rect.height,
            "Pokaż wykres", False, is_hovered  # Zmieniona nazwa przycisku
        )

        # Przycisk powrotu
        back_button_rect = pygame.Rect(
            self.config['width'] // 2 - 100, self.config['height'] - 60, 200, 50
        )
        is_hovered_back = back_button_rect.collidepoint(mouse_pos)
        self.draw_button(
            back_button_rect.x, back_button_rect.y,
            back_button_rect.width, back_button_rect.height,
            "Powrót (ESC)", False, is_hovered_back
        )

        return plot_button_rect, back_button_rect

    def game_over(self):
        """Obsługuje zakończenie gry."""
        if self.score > self.high_score:
            self.high_score = self.score
        save_score(self.player_name, self.score)
        self.scores_data = load_scores()
        self.game_active = False
        self.menu_active = True

    def reset_game(self):
        """Resetuje stan gry do początkowego."""
        self.bird.reset()
        self.pipes.reset()
        self.score = 0

    def run(self):
        """Główna pętla gry."""
        running = True
        while running:
            running = self.handle_events()
            self.update()
            self.render()
            self.clock.tick(self.config['fps'])

        pygame.quit()