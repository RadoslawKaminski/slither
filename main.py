import pygame
import random
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
width, height = 1200, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game - Slither.io Style")

# Parametry mapy
map_size = 4000  # Mapa większa niż okno gry
map_center = map_size / 2
camera_x, camera_y = 0, 0  # Początkowa pozycja kamery (wąż w centrum)
camera_speed = 15  # Szybkość poruszania się kamery

# Promień granicy mapy
boundary_radius = map_center

# Kolory
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Parametry węża
initial_size = 20  # Początkowy rozmiar węża (większy od jedzenia)
growth_rate = 2    # O ile wąż rośnie w każdym wymiarze po zjedzeniu
snake_size = initial_size  # Rozmiar węża
snake_speed = 12  # Stała prędkość węża
turn_factor = 9

# Parametry jedzenia
food_size = 9  # Rozmiar jedzenia (mniejsze niż wąż)

# Grubość węża
snake_body = [(map_center, map_center)]  # Wąż zaczyna na środku mapy (center of the map)
angle = 0  # Kąt węża, początkowo skierowany w prawo
turning = 0  # Kontrolowanie, czy strzałka jest trzymana

# Funkcja do rysowania węża
def draw_snake(snake_body, snake_size, offset_x, offset_y):
    for segment in snake_body:
        # Przesunięcie węża względem offsetu kamery
        pygame.draw.circle(screen, GREEN, (segment[0] - offset_x, segment[1] - offset_y), snake_size // 2)

# Funkcja do rysowania jedzenia
def draw_food(food_pos, food_size, offset_x, offset_y):
    pygame.draw.rect(screen, RED, pygame.Rect(food_pos[0] - offset_x, food_pos[1] - offset_y, food_size, food_size))

# Funkcja do generowania jedzenia w losowym miejscu wewnątrz granicy
def generate_food():
    # Losowanie punktu w obrębie koła
    angle = random.uniform(0, 2 * math.pi)
    radius = random.uniform(0, boundary_radius - food_size)
    x = map_size / 2 + radius * math.cos(angle)
    y = map_size / 2 + radius * math.sin(angle)
    return (x, y)

# Funkcja do obliczania ruchu węża z stałą prędkością
def move_snake(angle, snake_head):
    dx = math.cos(math.radians(angle)) * snake_speed
    dy = math.sin(math.radians(angle)) * snake_speed
    return (snake_head[0] + dx, snake_head[1] + dy)

# Główna pętla gry
clock = pygame.time.Clock()
running = True

# Lista pozycji jedzenia
food_positions = [generate_food() for _ in range(100)]  # 100 punktów jedzenia na mapie

while running:
    screen.fill(BLACK)  # Czyszczenie ekranu

    # Sprawdzenie zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                turning = -turn_factor  # Obrót w lewo
            if event.key == pygame.K_RIGHT:
                turning = turn_factor  # Obrót w prawo
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                turning = 0  # Zatrzymanie obrotu po puszczeniu strzałki

    # Zmieniamy kąt węża w zależności od trzymania strzałki
    angle += turning

    # Ograniczamy kąt węża, by nie zrobił za dużego skoku
    angle = angle % 360  # Kąt w zakresie 0-360°

    # Ruch węża: obliczanie nowej pozycji głowy na podstawie kąta (z stałą prędkością)
    head_x, head_y = snake_body[0]
    new_head = move_snake(angle, (head_x, head_y))

    # Dodanie nowej głowy i usunięcie ogona (ruch węża)
    snake_body = [new_head] + snake_body[:-1]

    # Sprawdzanie kolizji z jedzeniem
    for food_pos in food_positions[:]:
        if math.hypot(new_head[0] - food_pos[0], new_head[1] - food_pos[1]) < snake_size:
            snake_body.append(snake_body[-1])  # Dodajemy segment ciała
            food_positions.remove(food_pos)  # Usuwamy zjedzone jedzenie
            food_positions.append(generate_food())  # Generujemy nowe jedzenie

            # Wąż rośnie w szerz i w długość
            snake_size += growth_rate  # Zwiększamy rozmiar węża

    # Sprawdzanie kolizji z granicą (okrąg)
    head_x, head_y = snake_body[0]
    distance_from_center = math.hypot(head_x - map_size // 2, head_y - map_size // 2)

    if distance_from_center > boundary_radius:
        print("Collision with boundary!")
        running = False  # Koniec gry

    # Kamera podążająca za wężem (wąż zawsze w centrum)
    camera_x = head_x - width // 2
    camera_y = head_y - height // 2

    # Rysowanie węża i jedzenia (przesuniętych względem kamery)
    draw_snake(snake_body, snake_size, camera_x, camera_y)
    for food_pos in food_positions:
        draw_food(food_pos, food_size, camera_x, camera_y)

    # Rysowanie granicy mapy (czerwony okrąg) - uwzględnia przesunięcie kamery
    pygame.draw.circle(screen, RED,
                       (map_size // 2 - camera_x, map_size // 2 - camera_y),
                       boundary_radius, 2)

    # Aktualizacja okna
    pygame.display.update()

    # Kontrola szybkości gry
    clock.tick(30)  # Prędkość gry niezależna od rozmiaru węża

# Zakończenie gry
pygame.quit()
