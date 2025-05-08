# from OpenGL.GL import *
# import math

# def draw_rectangle(x, y, width, height, color=(1, 1, 1)):
#     glColor3f(*color)
#     glBegin(GL_QUADS)
#     glVertex2f(x, y)
#     glVertex2f(x + width, y)
#     glVertex2f(x + width, y + height)
#     glVertex2f(x, y + height)
#     glEnd()

# def draw_circle(cx, cy, radius, color=(1, 1, 1), segments=64):
#     glColor3f(*color)
#     glBegin(GL_TRIANGLE_FAN)
#     glVertex2f(cx, cy)
#     for i in range(segments + 1):
#         angle = 2 * math.pi * i / segments
#         x = cx + math.cos(angle) * radius
#         y = cy + math.sin(angle) * radius
#         glVertex2f(x, y)
#     glEnd()

# def draw_ellipse(cx, cy, rx, ry, color=(1, 1, 1), segments=64):
#     glColor3f(*color)
#     glBegin(GL_TRIANGLE_FAN)
#     glVertex2f(cx, cy)
#     for i in range(segments + 1):
#         angle = 2 * math.pi * i / segments
#         x = cx + math.cos(angle) * rx
#         y = cy + math.sin(angle) * ry
#         glVertex2f(x, y)
#     glEnd()
