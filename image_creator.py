from PIL import Image, ImageDraw
import random
WIDTH = 512
HEIGHT = 512
CIRCLES_AMOUNT = 1000
MAX_RADIUS = 12
N_OF_GENERATION = int(input("Enter number of iterations(~20k recommended, it will take 10-20 minutes)"))

def fitness_function(sketch, origin, lower_x, lower_y, upper_x, upper_y):
    if lower_x < 0:
        lower_x = 0
    if lower_y < 0:
        lower_y = 0
    if upper_x > WIDTH:
        upper_x = WIDTH
    if upper_y > HEIGHT:
        upper_y = HEIGHT
    square_difference = 0
    for i in range(lower_x, upper_x):
        for j in range(lower_y, upper_y):
            temp1 = sketch.getpixel((i, j))
            temp2 = origin.getpixel((i, j))
            a = 0
            if type(temp2) == type(a):
                temp2 = (temp2, temp2, temp2)

            square_difference += (temp1[0] - temp2[0]) ** 2 + (temp1[1] - temp2[1]) ** 2 + (temp1[2] - temp2[2]) ** 2
    return square_difference


def draw_circles(draw):
    for i in range(CIRCLES_AMOUNT):
        draw.ellipse((circles[i][0], circles[i][1], circles[i][0] +
                      circles[i][2] * 2, circles[i][1] + circles[i][2] * 2), circles[i][3])


def annealing(mid, min, max, i):
    lower = mid - int(max * (N_OF_GENERATION - i + 1) * (1 / (2 * N_OF_GENERATION)))
    upper = mid + int(max * (N_OF_GENERATION - i + 1) * (1 / (2 * N_OF_GENERATION)))
    if lower < min:
        lower = min
    if upper > max:
        upper = max
    return lower, upper


origin = Image.open("resources/sample16.tiff")

sketch = Image.new("RGB", (WIDTH, HEIGHT), "#000000")
draw = ImageDraw.Draw(sketch)

circles = []
#   creating initial circles
for i in range(CIRCLES_AMOUNT):
    first_point_x = random.randint(-1 * MAX_RADIUS, WIDTH)
    first_point_y = random.randint(-1 * MAX_RADIUS, HEIGHT)
    radius = random.randint(8, MAX_RADIUS)

    circles.append([first_point_x, first_point_y, radius, "#000000"])

fitness = fitness_function(sketch, origin, 1, 1, WIDTH, HEIGHT)
for i in range(N_OF_GENERATION):
    n = i % CIRCLES_AMOUNT

    prev1 = circles[n][0]
    prev2 = circles[n][1]
#   clearing the picture before drawing current circles
    draw.rectangle((1, 1, WIDTH, HEIGHT), "#000000")
    draw_circles(draw)

    circles[n][0] = random.randint(prev1 - MAX_RADIUS, prev1 + MAX_RADIUS)
    circles[n][1] = random.randint(prev2 - MAX_RADIUS, prev2 + MAX_RADIUS)

    old_fitness1 = fitness_function(sketch, origin, circles[n][0], circles[n][1],
                                    circles[n][0] + 2 * circles[n][2], circles[n][1] + 2 * circles[n][2])
    old_fitness2 = fitness_function(sketch, origin, prev1, prev2,
                                    prev1 + 2 * circles[n][2], prev2 + 2 * circles[n][2])

    draw.rectangle((1, 1, WIDTH, HEIGHT), "#000000")
    draw_circles(draw)

    new_fitness1 = fitness_function(sketch, origin, circles[n][0], circles[n][1],
                                    circles[n][0] + 2 * circles[n][2], circles[n][1] + 2 * circles[n][2])
    new_fitness2 = fitness_function(sketch, origin, prev1, prev2,
                                    prev1 + 2 * circles[n][2], prev2 + 2 * circles[n][2])

    if new_fitness1 + new_fitness2 - old_fitness1 - old_fitness2 > 0:
        circles[n][0] = prev1
        circles[n][1] = prev2
    else:
        fitness = fitness + new_fitness1 + new_fitness2 - old_fitness1 - old_fitness2

#   changing color trying to perform simulated annealing
    color = circles[n][3]
    values = tuple(int(color.lstrip('#')[i:i + 2], 16) for i in (0, 2, 4))
    lower_r, upper_r = annealing(values[0], 0, 255, i)
    lower_g, upper_g = annealing(values[1], 0, 255, i)
    lower_b, upper_b = annealing(values[2], 0, 255, i)
    lower_color = lower_r * 16 ** 4 + lower_g * 16 ** 2 + lower_b
    upper_color = upper_r * 16 ** 4 + upper_g * 16 ** 2 + upper_b

    draw.rectangle((1, 1, WIDTH, HEIGHT), "#000000")
    draw_circles(draw)
    old_fitness = fitness_function(sketch, origin, circles[n][0], circles[n][1],
                                    circles[n][0] + 2 * circles[n][2], circles[n][1] + 2 * circles[n][2])

    circles[n][3] = "#%06X" % random.randint(lower_color, upper_color)

    draw.rectangle((1, 1, WIDTH, HEIGHT), "#000000")
    draw_circles(draw)
    new_fitness = fitness_function(sketch, origin, circles[n][0], circles[n][1],
                                   circles[n][0] + 2 * circles[n][2], circles[n][1] + 2 * circles[n][2])
    if new_fitness - old_fitness > 0:
        circles[n][3] = color
    else:
        fitness = fitness + new_fitness - old_fitness

    if (i+1) % 100 == 0:
        sketch.save("output.png")
        print("Mutation number:" + str(i+1))
