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
zoom_factor = 0.03  # Im mniejsza wartość, tym mniejsze oddalanie

# Parametry mapy
map_size = 4000  # Mapa większa niż okno gry
map_center = map_size / 2
camera_x, camera_y = 0, 0  # Początkowa pozycja kamery (wąż w centrum)
camera_speed = 15  # Szybkość poruszania się kamery

# Parametr dla kratki
grid_spacing = 100  # Stała odległość między liniami kratki (przed skalowaniem)

# Promień granicy mapy
boundary_radius = map_center

# Kolory
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Parametry węża
initial_size = 30  # Początkowy rozmiar węża (większy od jedzenia)
growth_rate = 0.15    # O ile wąż rośnie w każdym wymiarze po zjedzeniu
snake_size = initial_size  # Rozmiar węża
snake_speed = 12  # Stała prędkość węża
turn_factor = 9

# Parametry jedzenia
food_size = 15  # Rozmiar jedzenia (mniejsze niż wąż)
segments_to_add = 0 # Zmienna przechowująca liczbę segmentów do dodania
# Parametry dużego jedzenia
large_food_size = 25  # Większy rozmiar dużego jedzenia
large_food_value = 3  # Dodaje wartość pięciu standardowych jedzeń

# Grubość węża
snake_body = [(map_center, map_center)]  # Wąż zaczyna na środku mapy (center of the map)
angle = 0  # Kąt węża, początkowo skierowany w prawo
turning = 0  # Kontrolowanie, czy strzałka jest trzymana

# Funkcja do rysowania oczu węża
def draw_eyes(snake_head, angle, offset_x, offset_y, scale):
    eye_offset_distance = 0.25 * snake_size
    eye_radius = int(0.2 * snake_size * scale)  # Rozmiar białego oka
    pupil_radius = int(0.1 * snake_size * scale)  # Rozmiar czarnej źrenicy

    # Pozycje oczu po lewej i prawej stronie głowy
    left_eye_x = snake_head[0] + eye_offset_distance * math.cos(math.radians(angle + 40))
    left_eye_y = snake_head[1] + eye_offset_distance * math.sin(math.radians(angle + 40))
    right_eye_x = snake_head[0] + eye_offset_distance * math.cos(math.radians(angle - 40))
    right_eye_y = snake_head[1] + eye_offset_distance * math.sin(math.radians(angle - 40))

    # Korekcja pozycji oczu względem kamery i skali
    left_eye_x = (left_eye_x - offset_x) * scale
    left_eye_y = (left_eye_y - offset_y) * scale
    right_eye_x = (right_eye_x - offset_x) * scale
    right_eye_y = (right_eye_y - offset_y) * scale

    # Obliczanie pozycji źrenic (lekko przesunięte w kierunku kursora)
    pupil_offset = 0.4 * eye_radius  # Przesunięcie źrenicy w kierunku kursora
    pupil_angle = math.radians(calculate_angle_to_mouse(snake_head, pygame.mouse.get_pos(), scale))

    # Pozycje źrenic
    left_pupil_x = left_eye_x + pupil_offset * math.cos(pupil_angle)
    left_pupil_y = left_eye_y + pupil_offset * math.sin(pupil_angle)
    right_pupil_x = right_eye_x + pupil_offset * math.cos(pupil_angle)
    right_pupil_y = right_eye_y + pupil_offset * math.sin(pupil_angle)

    # Rysowanie oczu
    pygame.draw.circle(screen, (255, 255, 255), (int(left_eye_x), int(left_eye_y)), eye_radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(right_eye_x), int(right_eye_y)), eye_radius)
    # Rysowanie źrenic
    pygame.draw.circle(screen, (0, 0, 0), (int(left_pupil_x), int(left_pupil_y)), pupil_radius)
    pygame.draw.circle(screen, (0, 0, 0), (int(right_pupil_x), int(right_pupil_y)), pupil_radius)

# Funkcja do generowania jedzenia w losowym miejscu wewnątrz granicy
def generate_food(is_large=False):
    x = random.uniform(0, map_size-50)
    y = random.uniform(0, map_size-50)
    from_center = math.hypot(x - map_size // 2, y - map_size // 2)
    if from_center > boundary_radius - 50 - (large_food_size if is_large else food_size) / 2:
        return generate_food(is_large)
    else:
        return (x, y)


# Funkcja do obliczania ruchu węża z stałą prędkością (głowy)
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
food_positions = [generate_food() for _ in range(400)]  # x punktów jedzenia na mapie
large_food_positions = [generate_food(is_large=True) for _ in range(1000)]  # x dużych jedzeń

while running:

    screen.fill(BLACK)  # Czyszczenie ekranu

    # Skala kamery zmienia się nieznacznie wraz z rozmiarem węża
    base_scale = 1  # Bazowy współczynnik skali
    scale = base_scale - math.sqrt(snake_size) * zoom_factor  # Skalowanie maleje z wielkością węża (math.log?)
    scale = max(0.2, scale)  # Ustawienie minimalnej skali, aby nie było za mało widoczne

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
            segments_to_add += 1  # Dodajemy jeden segment do kolejki do dodania
            food_positions.remove(food_pos)  # Usuwamy zjedzone jedzenie
            food_positions.append(generate_food())  # Generujemy nowe jedzenie

            # Wąż rośnie w szerz i w długość
            snake_size += growth_rate  # Zwiększamy rozmiar węża

    # Sprawdzanie kolizji z dużym jedzeniem
    for large_food_pos in large_food_positions[:]:
        if math.hypot(new_head[0] - large_food_pos[0], new_head[1] - large_food_pos[1]) < (
                snake_size / 2 + large_food_size / 2):
            segments_to_add += large_food_value  # Dodajemy kilka segmentów do kolejki
            large_food_positions.remove(large_food_pos)
            large_food_positions.append(generate_food(is_large=True))
            snake_size += growth_rate * large_food_value

    # Dodawanie segmentów w każdej iteracji, jeśli są segmenty do dodania
    if segments_to_add > 0:
        snake_body.append(snake_body[-1])  # Dodanie segmentu na końcu węża
        segments_to_add -= 1  # Zmniejszenie liczby segmentów do dodania

    # Sprawdzanie kolizji z granicą (uwzględniając rozmiar węża)
    distance_from_center = math.hypot(head_x - map_size // 2, head_y - map_size // 2)

    if distance_from_center > boundary_radius - snake_size / 2:
        print("Collision with boundary!")
        running = False  # Koniec gry

    # Ustawienie środka kamery względem pozycji głowy węża
    camera_x = head_x - (width // 2) / scale
    camera_y = head_y - (height // 2) / scale

    # Obliczamy, ile linii kratki jest widocznych przed przeskalowaniem
    visible_width = width / scale
    visible_height = height / scale

    # Obliczamy, od którego punktu zacząć rysowanie kratki w przestrzeni świata
    world_start_x = camera_x - (camera_x % grid_spacing)
    world_start_y = camera_y - (camera_y % grid_spacing)

    # Obliczamy, ile linii potrzebujemy
    lines_x = int(visible_width / grid_spacing) + 2
    lines_y = int(visible_height / grid_spacing) + 2

    # Rysujemy linie pionowe
    for i in range(lines_x):
        world_x = world_start_x + (i * grid_spacing)
        screen_x = (world_x - camera_x) * scale
        pygame.draw.line(screen, (50, 50, 50),
                         (int(screen_x), 0),
                         (int(screen_x), height))

    # Rysujemy linie poziome
    for i in range(lines_y):
        world_y = world_start_y + (i * grid_spacing)
        screen_y = (world_y - camera_y) * scale
        pygame.draw.line(screen, (50, 50, 50),
                         (0, int(screen_y)),
                         (width, int(screen_y)))

    # Rysowanie węża z uwzględnieniem skali
    for segment in snake_body:
        # Pozycjonowanie segmentów względem skalowanej kamery
        x = (segment[0] - camera_x) * scale
        y = (segment[1] - camera_y) * scale
        pygame.draw.circle(screen, GREEN, (int(x), int(y)), int(snake_size // 2 * scale))

    draw_eyes(new_head, angle, camera_x, camera_y, scale)

    # Rysowanie jedzenia
    for food_pos in food_positions:
        x = (food_pos[0] - camera_x) * scale
        y = (food_pos[1] - camera_y) * scale
        pygame.draw.circle(screen, RED, (int(x), int(y)), int(food_size // 2 * scale))

    # Rysowanie dużego jedzenia w głównej pętli gry
    for large_food_pos in large_food_positions:
        l_x = int((large_food_pos[0] - camera_x) * scale)
        l_y = int((large_food_pos[1] - camera_y) * scale)
        pygame.draw.circle(screen, (255, 140, 0),(l_x, l_y), large_food_size // 2 * scale)

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
