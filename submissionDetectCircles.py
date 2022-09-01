import numpy as np
from skimage.color import rgb2gray
from skimage.feature import canny
from scipy import ndimage
from imageio import imread
import matplotlib.pyplot as plt


def detect_circles(img, radius, use_gradient, sigma = 5 , upper_threshold = .9):
    gray = rgb2gray(img)
    edges = canny(gray, sigma=sigma)
    width, height = tuple(edges.shape)
    diffWidth = int(round(width))
    diffHeight = int(round(height))
    edge1D = []

    for i in range(width):
        for j in range(height):
            if edges[i][j]:
                edge1D += [(i, j)]
    accumulator = np.zeros((diffWidth, diffHeight))

    if use_gradient:
        weightX = np.array([[1, 0, -1], [1, 0, -1], [1, 0, -1]])
        weightY = np.array([[1, 1, 1], [0, 0, 0], [-1, -1, -1]])

        gx = ndimage.correlate(gray, weightX, mode='constant')
        gy = ndimage.correlate(gray, weightY, mode='constant')
        for edge in edge1D:
            x, y = tuple(edge)
            theta = np.arctan2(gx[x][y], gy[x][y])
            a = x + radius * np.cos(theta)
            b = y + radius * np.sin(theta)
            a2 = x - radius * np.cos(theta)
            b2 = y - radius * np.sin(theta)
            if 0 < a < width and height > b > 0:
                accumulator[int(a)][int(b)] += 1
            if 0 < a2 < width and height > b2 > 0:
                accumulator[int(a2)][int(b2)] += 1
    if not use_gradient:
        for edge in edge1D:
            for theta in range(360):
                x, y = tuple(edge)
                a = x - radius * np.cos(theta * np.pi / 180)
                b = y + radius * np.sin(theta * np.pi / 180)
                if 0 <= a < width and height > b >= 0:
                    accumulator[int(a)][int(b)] += 1
    centers = []
    threshold = np.max(accumulator) * 4 / 10
    for i in range(diffWidth):
        for j in range(diffHeight):
            if accumulator[i][j] < threshold:
                accumulator[i][j] = 0
    noMore = True
    upperThreshold = np.max(accumulator) * upper_threshold
    while noMore:
        nextMax = np.unravel_index(np.argmax(accumulator), accumulator.shape)
        t, u = tuple(nextMax)
        if accumulator[t][u] > (upperThreshold):
            if 10 < u < (diffHeight - 10) and (diffWidth - 10) > t > 10:
                for i in range(-10,11):
                    for j in range(-10,10):
                        if i == 0 and j == 0:
                            continue
                        accumulator[t+i][u+j] = 0
            if 5 < u < (diffHeight - 5) and (diffWidth - 5) > t > 5:
                for i in range(-5,6):
                    for j in range(-5,6):
                        if i == 0 and j == 0:
                            continue
                        accumulator[t+i][u+j] = 0

            centers += [(t, u)]
            accumulator[t][u] = 0
        else:
            noMore = False
    return centers


def draw_circles(img, centers, filename, title, radius):
    circles = []
    for center in centers:
        m, n = tuple(center)
        circles += [plt.Circle((n, m), radius, color='r', fill=False)]
    fig, ax = plt.subplots(1)
    ax.imshow(img)
    for circle in circles:
        ax.add_patch(circle)
    ax.set_title(title)
    fig.savefig(filename)


'''img = imread("./jupiter.jpg")
img2 = imread("./egg.jpg")
radiusJup3 = 110
radiusJup2 = 54
radiusJup1 = 32
radiusJup0 = 11
radiusEgg3 = 70
radiusEgg2 = 8
radiusEgg1 = 5
centers1 = detect_circles(img, radiusJup3, True, 5, .9)
centers2 = detect_circles(img, radiusJup2, True, 5, .9)
centers3 = detect_circles(img, radiusJup1, True, 5, .9)
centers4 = detect_circles(img, radiusJup0, True, 5, .9)
draw_circles(img, centers1, 'JupiterR110T', 'Jupiter Circle   Radius = 110, use_gradient = True', radiusJup3)
draw_circles(img, centers2, 'JupiterR54T', 'Jupiter Circle   Radius = 54, use_gradient = True', radiusJup2)
draw_circles(img, centers3, 'JupiterR32T', 'Jupiter Circle   Radius = 32, use_gradient = True', radiusJup1)
draw_circles(img, centers4, 'JupiterR11T', 'Jupiter Circle   Radius = 11, use_gradient = True', radiusJup0)
centers5 = detect_circles(img2, radiusEgg1, True, 3, .7)
centers6 = detect_circles(img2, radiusEgg2, True, 3, .7)
centers7 = detect_circles(img2, radiusEgg3, True, 3, .7)
draw_circles(img2, centers5, 'EggR5T', 'Egg Circles   Radius = 5, use_gradient = True', radiusEgg1)
draw_circles(img2, centers6, 'EggR8T', 'Egg Circles   Radius = 8, use_gradient = True', radiusEgg2)
draw_circles(img2, centers7, 'EggR70T', 'Egg Circles   Radius = 70, use_gradient = True', radiusEgg3)
centers8 = detect_circles(img, radiusJup3, False, 5, .9)
centers9 = detect_circles(img, radiusJup2, False, 5, .9)
centers10 = detect_circles(img, radiusJup1, False, 5, .9)
centers11 = detect_circles(img, radiusJup0, False, 5, .9)
draw_circles(img, centers8, 'JupiterR110F', 'Jupiter Circle   Radius = 110, use_gradient = False', radiusJup3)
draw_circles(img, centers9, 'JupiterR54F', 'Jupiter Circle   Radius = 54, use_gradient = False', radiusJup2)
draw_circles(img, centers10, 'JupiterR32F', 'Jupiter Circle   Radius = 32, use_gradient = False', radiusJup1)
draw_circles(img, centers11, 'JupiterR11F', 'Jupiter Circle   Radius = 11, use_gradient = False', radiusJup0)
centers12 = detect_circles(img2, radiusEgg1, False, 3, .7)
centers13 = detect_circles(img2, radiusEgg2, False, 3, .7)
centers14 = detect_circles(img2, radiusEgg3, False, 3, .7)
draw_circles(img2, centers12, 'EggR5F', 'Egg Circles   Radius = 5, use_gradient = False', radiusEgg1)
draw_circles(img2, centers13, 'EggR8F', 'Egg Circles   Radius = 8, use_gradient = False', radiusEgg2)
draw_circles(img2, centers14, 'EggR70F', 'Egg Circles   Radius = 70, use_gradient = False', radiusEgg3)'''



