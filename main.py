import pygame
import os
import math
from matrix import matrix_multiplication
from tkinter import *
from tkinter.filedialog import askopenfilename

os.environ["SDL_VIDEO_CENTERED"] = '1'
BLACK, WHITE, BLUE, GREEN, RED, GRAY, SILVER = (20, 20, 20), (230, 230, 230), (0, 154, 255), \
                                               (38, 230, 0), (255, 0, 0), (128, 128, 128), (192, 192, 192)
LINE_THICKNESS = 2
WIDTH, HEIGHT = 1200, 800
FPS = 60
SCALE = 600
SPEED = 0.05
RADIAN = 180 / math.pi

pygame.init()
pygame.display.set_caption("OBJren")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
font = pygame.font.SysFont("monospace", 24, bold=True)
clock = pygame.time.Clock()

pos_x, pos_y, old_x, old_y = 0, 0, 0, 0
angles = [0, 0, 0]
position = [WIDTH // 2, HEIGHT // 2]
drag_counter = 0
building = False  # used for drawing objects, False -> no drawing
lines = []
points = []
projected_points = []


def get_file():
    root = Tk()
    root.withdraw()
    path = askopenfilename()
    root.destroy()
    return path


# Imports obj if valid format
def import_obj():
    global points, lines, projected_points, angles, distance
    name = get_file()
    points = []
    lines = []
    distance = 15.1
    if name == '':
        return False
    f = open(name, "r")
    for line in f:
        if line[0] == "v":
            p = line[2:].split()
            p = [[float(x)] for x in p]
            points.append(p)
        if line[0] == "f":
            if line.find("/") != -1:
                print("Invalid format - please try again")
                import_obj()
                return False
            p = line[2:].split()
            p = [int(k) - 1 for k in p]

            for i in range(len(p)):
                if i == len(p) - 1:
                    lines.append([p[i], p[-1]])
                else:
                    lines.append([p[i], p[i + 1]])

    angles = [0, 0, 0]
    projected_points = [j for j in range(len(points))]


def connect_point(i, j, k):
    a = k[i]
    b = k[j]
    pygame.draw.line(screen, BLACK, (a[0], a[1]), (b[0], b[1]), LINE_THICKNESS)


unit = [[1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]]

x_matrix = unit
y_matrix = unit
z_matrix = unit

x_text = font.render('X-rotation: Use    and      arrow keys', True, BLACK)
y_text = font.render('Y-rotation: Use      and       arrow keys', True, BLACK)
z_text = font.render('Z-rotation: Use   and  ', True, BLACK)
depth_text = font.render('Depth/POV: Use mouse wheel', True, BLACK)
camera_text = font.render('Camera: Click and drag', True, BLACK)
button = pygame.Rect(20, 140, 200, 50)
button_shade = pygame.Rect(25, 145, 200, 50)
insert_txt = font.render('IMPORT OBJ', True, BLACK)

count = 0
distance = 15.1
drag = False
run = True
while run:
    clock.tick(FPS)
    screen.fill(WHITE)
    x_button, y_button = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4:
                distance -= 2
            if event.button == 5:
                distance += 2
            if event.button == 1:
                if button.collidepoint(x_button, y_button):
                    import_obj()
                    # building = True # keep commented for no drawing effect
                else:
                    drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            drag = False

    right_text = font.render('right', True, BLACK)
    left_text = font.render('left', True, BLACK)
    up_text = font.render('up', True, BLACK)
    down_text = font.render('down', True, BLACK)
    letter_z_text = font.render('Z', True, BLACK)
    letter_x_text = font.render('X', True, BLACK)

    rotation_x = [[1, 0, 0],
                  [0, math.cos(angles[1]), -math.sin(angles[1])],
                  [0, math.sin(angles[1]), math.cos(angles[1])]]

    rotation_x2 = [*zip(*rotation_x)]

    rotation_y = [[math.cos(angles[0]), 0, -math.sin(angles[0])],
                  [0, 1, 0],
                  [math.sin(angles[0]), 0, math.cos(angles[0])]]

    rotation_y2 = [*zip(*rotation_y)]

    rotation_z = [[math.cos(angles[2]), -math.sin(angles[2]), 0],
                  [math.sin(angles[2]), math.cos(angles[2]), 0],
                  [0, 0, 1]]

    rotation_z2 = [*zip(*rotation_z)]

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        y_matrix = rotation_y2
        angles[0] -= SPEED
        left_text = font.render('left', True, GREEN)
    if keys[pygame.K_RIGHT]:
        y_matrix = rotation_y2
        angles[0] += SPEED
        right_text = font.render('right', True, GREEN)
    if keys[pygame.K_UP]:
        x_matrix = rotation_x2
        angles[1] -= SPEED
        up_text = font.render('up', True, GREEN)
    if keys[pygame.K_DOWN]:
        x_matrix = rotation_x2
        angles[1] += SPEED
        down_text = font.render('down', True, GREEN)
    if keys[pygame.K_z]:
        z_matrix = rotation_z2
        angles[2] -= SPEED
        letter_z_text = font.render('Z', True, GREEN)
    if keys[pygame.K_x]:
        z_matrix = rotation_z2
        angles[2] += SPEED
        letter_x_text = font.render('X', True, GREEN)

    # Position adjustment
    if drag:
        drag_counter += 1
        if drag_counter == 1:
            old_x, old_y = pygame.mouse.get_pos()
        else:
            x, y = pygame.mouse.get_pos()
            pos_x = old_x - x
            pos_y = old_y - y
            old_x = x
            old_y = y
    else:
        pos_x, pos_y, old_x, old_y, drag_counter = 0, 0, 0, 0, 0

    position[0] -= pos_x
    position[1] -= pos_y

    for i in range(len(angles)):
        if angles[i] >= 2 * math.pi:
            angles[i] = 0
        elif angles[i] < 0:
            angles[i] = 2 * math.pi

    index = 0
    for point in points:
        rotated_2d = matrix_multiplication(matrix_multiplication(rotation_z, matrix_multiplication(y_matrix, x_matrix)),
                                           point)

        z = 1 / (distance - rotated_2d[2][0])
        projection_matrix = [[z, 0, 0],
                             [0, -z, 0]]
        projected_2d = matrix_multiplication(projection_matrix, rotated_2d)

        x = int(projected_2d[0][0] * SCALE) + position[0]
        y = int(projected_2d[1][0] * SCALE) + position[1]
        projected_points[index] = [x, y]
        pygame.draw.circle(screen, RED, (x, y), 2)
        index += 1

    if building:
        building_img = font.render(f'BUILDING OBJECT', True, BLACK)
        screen.blit(building_img, (20, 20))

    for line in lines:
        connect_point(line[0], line[1], projected_points)
        if building:
            pygame.display.update()
    building = False

    if button.collidepoint(x_button, y_button):
        button = pygame.Rect(22, 142, 200, 50)
        pygame.draw.rect(screen, GRAY, button_shade)
        pygame.draw.rect(screen, SILVER, button)

        screen.blit(insert_txt, (48, 152))
    else:
        button = pygame.Rect(20, 140, 200, 50)

        pygame.draw.rect(screen, GRAY, button_shade)
        pygame.draw.rect(screen, SILVER, button)
        screen.blit(insert_txt, (46, 150))

    angle_a = font.render(f'α: {round(angles[0] * RADIAN, 3)}°', True, BLACK)
    angle_b = font.render(f'β: {round(angles[1] * RADIAN, 3)}°', True, BLACK)
    angle_c = font.render(f'σ: {round(angles[2] * RADIAN, 3)}°', True, BLACK)
    screen.blit(y_text, (20, 60))
    screen.blit(left_text, (245, 60))
    screen.blit(right_text, (370, 60))
    screen.blit(x_text, (20, 20))
    screen.blit(up_text, (245, 20))
    screen.blit(down_text, (342, 20))
    screen.blit(z_text, (20, 100))
    screen.blit(letter_z_text, (245, 100))
    screen.blit(letter_x_text, (327, 100))
    screen.blit(angle_a, (WIDTH - 300, 20))
    screen.blit(angle_b, (WIDTH - 300, 60))
    screen.blit(angle_c, (WIDTH - 300, 100))
    screen.blit(camera_text, (20, HEIGHT - 80))
    screen.blit(depth_text, (20, HEIGHT - 40))

    pygame.display.update()

pygame.quit()
