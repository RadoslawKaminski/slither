import pygame
import random
import math

# Inicjalizacja Pygame
pygame.init()

# Ustawienia okna
width, height = 1500, 1000
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Snake Game - Slither.io Style")

# Współczynnik zmiany skali kamery w zależności od rozmiaru węża
zoom_factor = 0.03  # Im mniejsza wartość, tym mniejsze oddalanie
current_scale = 1

# Parametry mapy
map_size = 4000
map_center = map_size / 2
camera_x, camera_y = 0, 0
camera_speed = 15

# Parametr dla kratki
grid_spacing = 100

# Promień granicy mapy
boundary_radius = map_center

# Kolory
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
RED = (255, 0, 0)

# Parametry węża
initial_size = 30
growth_rate = 0.15
snake_size = initial_size
snake_speed = 12

# Parametry jedzenia
food_size = 15
segments_to_add = 0
large_food_size = 25
large_food_value = 30

# Grubość węża
snake_body = [(map_center, map_center)]  # Wąż zaczyna na środku mapy
angle = 0  # Kąt kierunku węża, początkowo skierowany w prawo
turning = 0  # Kontrolowanie, czy strzałka jest trzymana


class Food:
    def __init__(self, position, is_large=False):
        self.position = position
        self.is_large = is_large
        self.size = large_food_size if is_large else food_size
        self.color = (255, 140, 0) if is_large else RED

    def draw(self, screen, camera_x, camera_y, scale):
        x = (self.position[0] - camera_x) * scale
        y = (self.position[1] - camera_y) * scale
        pygame.draw.circle(screen, self.color, (int(x), int(y)), int(self.size // 2 * scale))


def generate_food(is_large=False):
    x = random.randint(0, map_size - 50)
    y = random.randint(0, map_size - 50)
    from_center = math.hypot(x - map_size // 2, y - map_size // 2)
    if from_center > boundary_radius - 50 - (large_food_size if is_large else food_size) / 2:
        return generate_food(is_large)
    return Food((x, y), is_large)


def draw_eyes(snake_head, angle, offset_x, offset_y, scale):
    eye_offset_distance = 0.25 * snake_size
    eye_radius = int(0.2 * snake_size * scale)  # Rozmiar białego oka
    pupil_radius = int(0.13 * snake_size * scale)  # Rozmiar czarnej źrenicy
    eyes_angle = 50

    left_eye_x = snake_head[0] + eye_offset_distance * math.cos(math.radians(angle + eyes_angle))
    left_eye_y = snake_head[1] + eye_offset_distance * math.sin(math.radians(angle + eyes_angle))
    right_eye_x = snake_head[0] + eye_offset_distance * math.cos(math.radians(angle - eyes_angle))
    right_eye_y = snake_head[1] + eye_offset_distance * math.sin(math.radians(angle - eyes_angle))

    left_eye_x = (left_eye_x - offset_x) * scale
    left_eye_y = (left_eye_y - offset_y) * scale
    right_eye_x = (right_eye_x - offset_x) * scale
    right_eye_y = (right_eye_y - offset_y) * scale

    # Obliczanie pozycji źrenic (lekko przesunięte w kierunku kursora)
    pupil_offset = 0.4 * eye_radius  # Przesunięcie źrenicy w kierunku kursora
    pupil_angle = math.radians(calculate_angle_to_mouse(snake_head, pygame.mouse.get_pos(), scale))

    left_pupil_x = left_eye_x + pupil_offset * math.cos(pupil_angle)
    left_pupil_y = left_eye_y + pupil_offset * math.sin(pupil_angle)
    right_pupil_x = right_eye_x + pupil_offset * math.cos(pupil_angle)
    right_pupil_y = right_eye_y + pupil_offset * math.sin(pupil_angle)

    pygame.draw.circle(screen, (255, 255, 255), (int(left_eye_x), int(left_eye_y)), eye_radius)
    pygame.draw.circle(screen, (255, 255, 255), (int(right_eye_x), int(right_eye_y)), eye_radius)
    pygame.draw.circle(screen, (0, 0, 0), (int(left_pupil_x), int(left_pupil_y)), pupil_radius)
    pygame.draw.circle(screen, (0, 0, 0), (int(right_pupil_x), int(right_pupil_y)), pupil_radius)


def move_snake(angle, snake_head):
    dx = math.cos(math.radians(angle)) * snake_speed
    dy = math.sin(math.radians(angle)) * snake_speed
    return snake_head[0] + dx, snake_head[1] + dy


using_mouse_control = True
prev_mouse_pos = pygame.mouse.get_pos()


def calculate_angle_to_mouse(snake_head, mouse_pos, scale):
    adjusted_mouse_x = (mouse_pos[0] / scale) + camera_x
    adjusted_mouse_y = (mouse_pos[1] / scale) + camera_y
    dx = adjusted_mouse_x - snake_head[0]
    dy = adjusted_mouse_y - snake_head[1]
    return math.degrees(math.atan2(dy, dx))


# Główna pętla gry
clock = pygame.time.Clock()
running = True

# Inicjalizacja jedzenia jako obiektów klasy Food
food_list = [generate_food() for _ in range(400)]
large_food_list = [generate_food(is_large=True) for _ in range(100)]

# Zmienne do interpolacji ruchu kamery
target_camera_x = camera_x
target_camera_y = camera_y
interpolation_speed = 0.1

while running:
    screen.fill(BLACK)

    base_scale = 1
    target_scale = base_scale - math.sqrt(snake_size) * zoom_factor
    target_scale = max(0.2, target_scale)

    # Interpolacja skali
    current_scale = current_scale + (target_scale - current_scale) * interpolation_speed
    scale = current_scale

    turn_factor = 70 / math.sqrt(snake_size)

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                turning = -turn_factor
                using_mouse_control = False
            if event.key == pygame.K_RIGHT:
                turning = turn_factor
                using_mouse_control = False
        if event.type == pygame.KEYUP:
            if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                turning = 0

    mouse_x, mouse_y = pygame.mouse.get_pos()
    head_x, head_y = snake_body[0]

    if (mouse_x, mouse_y) != prev_mouse_pos:
        using_mouse_control = True
    prev_mouse_pos = (mouse_x, mouse_y)

    if using_mouse_control:
        mouse_angle = calculate_angle_to_mouse((head_x, head_y), (mouse_x, mouse_y), scale)
        angle_difference = (mouse_angle - angle + 180) % 360 - 180
        if angle_difference < -turn_factor:
            angle -= turn_factor
        elif angle_difference > turn_factor:
            angle += turn_factor
        else:
            angle += angle_difference
    else:
        angle += turning

    angle = angle % 360
    new_head = move_snake(angle, (head_x, head_y))
    snake_body = [new_head] + snake_body[:-1]

    # Kolizje z jedzeniem
    for food in food_list[:]:
        if math.hypot(new_head[0] - food.position[0], new_head[1] - food.position[1]) < (
                snake_size / 2 + food.size / 2):
            segments_to_add += 1
            food_list.remove(food)
            food_list.append(generate_food())
            snake_size += growth_rate

    for large_food in large_food_list[:]:
        if math.hypot(new_head[0] - large_food.position[0], new_head[1] - large_food.position[1]) < (
                snake_size / 2 + large_food.size / 2):
            segments_to_add += large_food_value
            large_food_list.remove(large_food)
            large_food_list.append(generate_food(is_large=True))
            snake_size += growth_rate * large_food_value

    if segments_to_add > 0:
        snake_body.append(snake_body[-1])
        segments_to_add -= 1

    distance_from_center = math.hypot(head_x - map_size // 2, head_y - map_size // 2)
    if distance_from_center > boundary_radius - snake_size / 2:
        print("Collision with boundary!")
        running = False

    # Interpolacja ruchu kamery
    target_camera_x = head_x - (width // 2) / scale
    target_camera_y = head_y - (height // 2) / scale
    camera_x += (target_camera_x - camera_x) * interpolation_speed
    camera_y += (target_camera_y - camera_y) * interpolation_speed

    visible_width = width / scale
    visible_height = height / scale
    world_start_x = camera_x - (camera_x % grid_spacing)
    world_start_y = camera_y - (camera_y % grid_spacing)
    lines_x = int(visible_width / grid_spacing) + 2
    lines_y = int(visible_height / grid_spacing) + 2

    for i in range(lines_x):
        world_x = world_start_x + (i * grid_spacing)
        screen_x = (world_x - camera_x) * scale
        pygame.draw.line(screen, (50, 50, 50), (int(screen_x), 0), (int(screen_x), height))

    for i in range(lines_y):
        world_y = world_start_y + (i * grid_spacing)
        screen_y = (world_y - camera_y) * scale
        pygame.draw.line(screen, (50, 50, 50), (0, int(screen_y)), (width, int(screen_y)))

    # Rysowanie węża
    for segment in snake_body:
        x = (segment[0] - camera_x) * scale
        y = (segment[1] - camera_y) * scale
        pygame.draw.circle(screen, GREEN, (int(x), int(y)), int(snake_size // 2 * scale))

    draw_eyes(new_head, angle, camera_x, camera_y, scale)

    # Rysowanie jedzenia używając metody draw obiektów Food
    for food in food_list:
        food.draw(screen, camera_x, camera_y, scale)

    for large_food in large_food_list:
        large_food.draw(screen, camera_x, camera_y, scale)

    pygame.draw.circle(screen, RED,
                       (int((map_size // 2 - camera_x) * scale), int((map_size // 2 - camera_y) * scale)),
                       int(boundary_radius * scale), 2)

    pygame.display.update()
    clock.tick(30)

pygame.quit()