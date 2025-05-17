import pygame as pg
from OpenGL.GL import *

def render_text(text, font_size=24, color=(255, 255, 255)):
    font = pg.font.SysFont('Arial', font_size)

    # Render with anti-aliasing, white text, and transparent background
    text_surface = font.render(text, True, color)
    text_surface = text_surface.convert_alpha()  # Keep transparency

    # Flip vertically for OpenGL
    text_surface = pg.transform.flip(text_surface, False, True)

    texture_data = pg.image.tostring(text_surface, "RGBA", True)
    width, height = text_surface.get_size()

    tex_id = glGenTextures(1)
    glBindTexture(GL_TEXTURE_2D, tex_id)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_LINEAR)
    glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_LINEAR)
    glTexImage2D(GL_TEXTURE_2D, 0, GL_RGBA, width, height, 0, GL_RGBA, GL_UNSIGNED_BYTE, texture_data)

    return tex_id, width, height


