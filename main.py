import pygame
import os
import math
from matrix import matrix_multiplication
from tkinter import *
from tkinter.filedialog import askopenfilename

os.environ["SDL_VIDEO_CENTERED"] = '1'
black, white, blue, green, red, gray, silver = (20, 20, 20), (230, 230, 230), (0, 154, 255), \
                                               (38, 230, 0), (255, 0, 0), (128, 128, 128), (192, 192, 192)
# width, height = 1920, 1080
width, height = 1200, 800

pygame.init()

pygame.display.set_caption("OBJren")
screen = pygame.display.set_mode((width, height))
font = pygame.font.SysFont("monospace", 24, bold=True)

clock = pygame.time.Clock()
fps = 60

pos_x, pos_y, old_x, old_y = 0, 0, 0, 0
angles = [0, 0, 0]
position = [width // 2, height // 2]
scale = 600
speed = 0.05
radian = 180 / math.pi
drag_counter = 0
building = False  # set true to always draw objects
lines = []
points = []
projected_points = []


def get_file():
    root = Tk()
    root.withdraw()
    path = askopenfilename()
    root.destroy()
    return path


# Import
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
            # p[1][0] -= 20
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
    pygame.draw.line(screen, black, (a[0], a[1]), (b[0], b[1]), 2)


unit = [[1, 0, 0],
        [0, 1, 0],
        [0, 0, 1]]

xV = unit
yV = unit
zV = unit

imgX = font.render('X-rotation: Use    and      arrow keys', True, black)
imgY = font.render('Y-rotation: Use      and       arrow keys', True, black)
imgZ = font.render('Z-rotation: Use   and  ', True, black)
imgD = font.render('Depth/POV: Use mouse wheel', True, black)
imgC = font.render('Camera: Click and drag', True, black)
button = pygame.Rect(20, 140, 200, 50)
button_shade = pygame.Rect(25, 145, 200, 50)
insert_txt = font.render('IMPORT OBJ', True, black)

count = 0
distance = 15.1
drag = False
run = True
while run:
    clock.tick(fps)
    screen.fill(white)
    x_button, y_button = pygame.mouse.get_pos()
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            run = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 4: distance -= 2
            if event.button == 5: distance += 2
            if event.button == 1:
                if button.collidepoint(x_button, y_button):
                    import_obj()
                    # building = True # keep commented for no drawing effect
                else:
                    drag = True
        if event.type == pygame.MOUSEBUTTONUP:
            drag = False

    img_r = font.render('right', True, black)
    img_l = font.render('left', True, black)
    img_u = font.render('up', True, black)
    img_d = font.render('down', True, black)
    img_z = font.render('Z', True, black)
    img_x = font.render('X', True, black)

    rotation_x = [[1, 0, 0],
                  [0, math.cos(angles[1]), -math.sin(angles[1])],
                  [0, math.sin(angles[1]), math.cos(angles[1])]]

    rotation_x2 = [*zip(*rotation_x)]

    rotation_y = [[math.cos(angles[0]), 0, -math.sin(angles[0])],
                  [0, 1, 0],
                  [math.sin(angles[0]), 0, math.cos(angles[0])]]

    rotation_y2 = [*zip(*rotation_y)]
    #
    rotation_z = [[math.cos(angles[2]), -math.sin(angles[2]), 0],
                  [math.sin(angles[2]), math.cos(angles[2]), 0],
                  [0, 0, 1]]

    rotation_z2 = [*zip(*rotation_z)]

    keys = pygame.key.get_pressed()

    if keys[pygame.K_LEFT]:
        yV = rotation_y2
        angles[0] -= speed
        img_l = font.render('left', True, green)
    if keys[pygame.K_RIGHT]:
        yV = rotation_y2
        angles[0] += speed
        img_r = font.render('right', True, green)
    if keys[pygame.K_UP]:
        xV = rotation_x2
        angles[1] -= speed
        img_u = font.render('up', True, green)
    if keys[pygame.K_DOWN]:
        xV = rotation_x2
        angles[1] += speed
        img_d = font.render('down', True, green)
    if keys[pygame.K_z]:
        zV = rotation_z2
        angles[2] -= speed
        img_z = font.render('Z', True, green)
    if keys[pygame.K_x]:
        zV = rotation_z2
        angles[2] += speed
        img_x = font.render('X', True, green)

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
        rotated_2d = matrix_multiplication(matrix_multiplication(rotation_z, matrix_multiplication(yV, xV)), point)

        z = 1 / (distance - rotated_2d[2][0])
        projection_matrix = [[z, 0, 0],
                             [0, -z, 0]]
        projected_2d = matrix_multiplication(projection_matrix, rotated_2d)

        x = int(projected_2d[0][0] * scale) + position[0]
        y = int(projected_2d[1][0] * scale) + position[1]
        projected_points[index] = [x, y]
        pygame.draw.circle(screen, red, (x, y), 2)
        index += 1

    if building:
        building_img = font.render(f'BUILDING OBJECT', True, black)
        screen.blit(building_img, (20, 20))

    for line in lines:
        connect_point(line[0], line[1], projected_points)
        if building: pygame.display.update()
    building = False

    if button.collidepoint(x_button, y_button):
        button = pygame.Rect(22, 142, 200, 50)
        pygame.draw.rect(screen, gray, button_shade)
        pygame.draw.rect(screen, silver, button)

        screen.blit(insert_txt, (48, 152))
    else:
        button = pygame.Rect(20, 140, 200, 50)

        pygame.draw.rect(screen, gray, button_shade)
        pygame.draw.rect(screen, silver, button)
        screen.blit(insert_txt, (46, 150))

    img_a = font.render(f'α: {round(angles[0] * radian, 3)}°', True, black)
    img_b = font.render(f'β: {round(angles[1] * radian, 3)}°', True, black)
    img_c = font.render(f'σ: {round(angles[2] * radian, 3)}°', True, black)
    screen.blit(imgY, (20, 60))
    screen.blit(img_l, (245, 60))
    screen.blit(img_r, (370, 60))
    screen.blit(imgX, (20, 20))
    screen.blit(img_u, (245, 20))
    screen.blit(img_d, (342, 20))
    screen.blit(imgZ, (20, 100))
    screen.blit(img_z, (245, 100))
    screen.blit(img_x, (327, 100))
    screen.blit(img_a, (width - 300, 20))
    screen.blit(img_b, (width - 300, 60))
    screen.blit(img_c, (width - 300, 100))
    screen.blit(imgC, (20, height - 80))
    screen.blit(imgD, (20, height - 40))

    pygame.display.update()

pygame.quit()
