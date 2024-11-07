import pygame
import random
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
width, height = 1200, 900
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game - Slither.io Style")

# Współczynnik zmiany skali kamery w zależności od rozmiaru węża
zoom_factor = 0.0023  # Im mniejsza wartość, tym mniejsze oddalanie

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
initial_size = 30  # Początkowy rozmiar węża (większy od jedzenia)
growth_rate = 0.2    # O ile wąż rośnie w każdym wymiarze po zjedzeniu
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

# zmienna do śledzenia, czy używamy sterowania myszką
using_mouse_control = True
prev_mouse_pos = pygame.mouse.get_pos()  # Początkowa pozycja myszy

# Funkcja do obliczania kąta między głową węża a kursorem myszy, uwzględniając skalę kamery
def calculate_angle_to_mouse(snake_head, mouse_pos, scale):
    # Skorygowanie pozycji kursora do skali i położenia kamery
    adjusted_mouse_x = (mouse_pos[0] / scale) + camera_x
    adjusted_mouse_y = (mouse_pos[1] / scale) + camera_y

    # Obliczenie różnicy między głową a skorygowaną pozycją kursora
    dx = adjusted_mouse_x - snake_head[0]
    dy = adjusted_mouse_y - snake_head[1]

    return math.degrees(math.atan2(dy, dx))

# Główna pętla gry
clock = pygame.time.Clock()
running = True

# Lista pozycji jedzenia
food_positions = [generate_food() for _ in range(4000)]  # 100 punktów jedzenia na mapie

while running:

    # Skala kamery zmienia się nieznacznie wraz z rozmiarem węża
    base_scale = 1  # Bazowy współczynnik skali
    scale = base_scale - snake_size * zoom_factor  # Skalowanie maleje z wielkością węża
    scale = max(0.15, scale)  # Ustawienie minimalnej skali, aby nie było za mało widoczne

    screen.fill(BLACK)  # Czyszczenie ekranu

    # Sprawdzenie zdarzeń
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                turning = -turn_factor  # Obrót w lewo
                using_mouse_control = False  # Przestawienie na sterowanie klawiaturą
            if event.key == pygame.K_RIGHT:
                turning = turn_factor  # Obrót w prawo
                using_mouse_control = False  # Przestawienie na sterowanie klawiaturą
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                turning = 0  # Zatrzymanie obrotu po puszczeniu strzałki

    # Pobranie aktualnej pozycji kursora myszy
    mouse_x, mouse_y = pygame.mouse.get_pos()

    head_x, head_y = snake_body[0]

    # Włączenie sterowania myszką przy poruszeniu jej pozycji
    if (mouse_x, mouse_y) != prev_mouse_pos:
        using_mouse_control = True  # Włączenie sterowania myszką, gdy jest poruszana
    prev_mouse_pos = (mouse_x, mouse_y)  # Aktualizacja poprzedniej pozycji myszy

    # Obliczanie kąta do kursora myszy tylko wtedy, gdy używamy myszki
    if using_mouse_control:
        # Obliczanie kąta do kursora
        mouse_angle = calculate_angle_to_mouse((head_x, head_y), (mouse_x, mouse_y), scale)
        angle_difference = (mouse_angle - angle + 180) % 360 - 180  # Normalizacja różnicy do zakresu -180 do 180 stopni

        # Zmieniamy kąt węża, aby stopniowo zbliżać go do kąta kursora
        if angle_difference < -turn_factor:
            angle -= turn_factor
        elif angle_difference > turn_factor:
            angle += turn_factor
        else:
            angle += angle_difference  # Zbliżenie się do kursora, gdy różnica jest mniejsza niż `turn_factor`

    else:
        # Jeśli używamy klawiatury, aktualizujemy kąt bez użycia myszy
        angle += turning

    # Ograniczamy kąt węża, by nie zrobił za dużego skoku
    angle = angle % 360  # Kąt w zakresie 0-360°

    # Ruch węża: obliczanie nowej pozycji głowy na podstawie kąta (z stałą prędkością)
    new_head = move_snake(angle, (head_x, head_y))

    # Dodanie nowej głowy i usunięcie ogona (ruch węża)
    snake_body = [new_head] + snake_body[:-1]

    # Sprawdzanie kolizji z jedzeniem
    for food_pos in food_positions[:]:
        if math.hypot(new_head[0] - food_pos[0], new_head[1] - food_pos[1]) < (snake_size / 2 + food_size / 2):
            snake_body.append(snake_body[-1])  # Dodajemy segment ciała
            food_positions.remove(food_pos)  # Usuwamy zjedzone jedzenie
            food_positions.append(generate_food())  # Generujemy nowe jedzenie

            # Wąż rośnie w szerz i w długość
            snake_size += growth_rate  # Zwiększamy rozmiar węża

    # Sprawdzanie kolizji z granicą (uwzględniając rozmiar węża)
    head_x, head_y = snake_body[0]
    distance_from_center = math.hypot(head_x - map_size // 2, head_y - map_size // 2)

    if distance_from_center > boundary_radius - snake_size / 2:
        print("Collision with boundary!")
        running = False  # Koniec gry

    # Ustawienie środka kamery względem pozycji głowy węża
    camera_x = head_x - (width // 2) / scale
    camera_y = head_y - (height // 2) / scale

    # Rysowanie węża z uwzględnieniem skali
    for segment in snake_body:
        # Pozycjonowanie segmentów względem skalowanej kamery
        x = (segment[0] - camera_x) * scale
        y = (segment[1] - camera_y) * scale
        pygame.draw.circle(screen, GREEN, (int(x), int(y)), int(snake_size // 2 * scale))

    # Rysowanie jedzenia
    for food_pos in food_positions:
        x = (food_pos[0] - camera_x) * scale
        y = (food_pos[1] - camera_y) * scale
        pygame.draw.rect(screen, RED, pygame.Rect(int(x), int(y), int(food_size * scale), int(food_size * scale)))

    # Rysowanie granicy mapy (skalowany czerwony okrąg)
    pygame.draw.circle(screen, RED,
                       (int((map_size // 2 - camera_x) * scale), int((map_size // 2 - camera_y) * scale)),
                       int(boundary_radius * scale), 2)


    # Aktualizacja okna
    pygame.display.update()

    # Kontrola szybkości gry
    clock.tick(30)  # Prędkość gry niezależna od rozmiaru węża

# Zakończenie gry
pygame.quit()
