import pygame
from text_manager import render_text
from texture import draw_texture

class Zombie:
    def __init__(self, x, y, speed, word, zombie_texture, zombie_w, zombie_h):
        self.x = x
        self.y = y
        self.speed = speed
        self.word = word
        self.alive = True
        self.zombie_texture = zombie_texture
        self.zombie_w = zombie_w
        self.zombie_h = zombie_h
        self.text_texture, self.tw, self.th = render_text(self.word)

    def update(self, dt, player_right_edge, stop_distance):
        if not self.alive:
            return
        distance_to_player = self.x - player_right_edge
        if distance_to_player > stop_distance:
            self.x -= self.speed * dt
        return distance_to_player

    def process_typed_letter(self, typed_letter):
        if self.alive and self.word and typed_letter == self.word[0]:
            self.word = self.word[1:]
            pygame.display.get_surface()  # Ensure pygame is initialized
            from OpenGL.GL import glDeleteTextures
            glDeleteTextures([self.text_texture])
            if not self.word:
                self.alive = False
            else:
                self.text_texture, self.tw, self.th = render_text(self.word)
            return True
        return False

    def draw(self):
        if self.alive:
            draw_texture(self.zombie_texture, self.x, self.y, self.zombie_w * 1.5, self.zombie_h * 1.5)
            draw_texture(self.text_texture, self.x + 35, self.y - 25, self.tw, self.th) 