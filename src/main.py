import pygame as pg
from OpenGL.GL import *
from texture import load_texture, draw_texture, draw_rectangle
from text_manager import render_text

class App:
    def __init__(self):

        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 640, 480, 0, -1, 1)  
        glMatrixMode(GL_MODELVIEW)

        glClearColor(0.1, 0.2, 0.2, 1)
        self.sky_texture, self.sky_w, self.sky_h = load_texture("assets/images/sky.png")
        self.player_texture, self.player_w, self.player_h = load_texture("assets/images/player.png")
        self.zombie_texture, self.zombie_w, self.zombie_h = load_texture("assets/images/zombie.png")
        self.ground_texture, self.ground_w, self.ground_h = load_texture("assets/images/ground.png")
        
        self.player_x = 50
        self.player_y = 225
        self.player_speed = 5
        
        self.zombie_x = 500
        self.zombie_speed = 100  
        
        self.zombie_word = "zombie"
        self.typed_letters = ""
        self.text_texture, self.tw, self.th = render_text(self.zombie_word)
        self.word_complete = False  # Flag to track if word is finished
        
        self.bullets = []
        self.bullet_speed = 4000  # pixels per second

        self.mainLoop()
        
    def mainLoop(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT :
                    running = False
                elif event.type == pg.KEYDOWN:
                    typed_letter = event.unicode.lower()
                    if self.zombie_word and typed_letter == self.zombie_word[0]:
                        # Remove first letter from word
                        self.zombie_word = self.zombie_word[1:]
                        glDeleteTextures([self.text_texture])
                        if not self.zombie_word:  # If word is empty
                            self.word_complete = True
                        else:
                            self.text_texture, self.tw, self.th = render_text(self.zombie_word)

                        # Fire a bullet
                        self.bullets.append({'x': self.player_x + self.player_w // 2, 'y': self.player_y + 50})
                    
            dt = self.clock.tick(60) / 1000
            
            self.zombie_x -= self.zombie_speed * dt
            
            # Update bullets
            for bullet in self.bullets[:]:  # Create a copy of the list to safely remove items
                bullet['x'] += self.bullet_speed * dt
                # Check for collision with zombie
                if (bullet['x'] >= self.zombie_x and 
                    bullet['x'] <= self.zombie_x + self.zombie_w * 1.5 and
                    bullet['y'] >= 225 and 
                    bullet['y'] <= 225 + self.zombie_h * 1.5):
                    self.bullets.remove(bullet)
                    # Reset zombie position or handle zombie hit
                    # self.zombie_x = 500
                # Remove bullets that go off screen
                elif bullet['x'] > 640:
                    self.bullets.remove(bullet)
                                       
            glClear(GL_COLOR_BUFFER_BIT)
            draw_texture(self.sky_texture, 0, 0, self.sky_w, self.sky_h)
            draw_texture(self.ground_texture, 0, 0, self.ground_w // 2, self.ground_h // 1.5)
            draw_texture(self.player_texture, self.player_x, self.player_y, self.player_w * 1.5, self.player_h * 1.5)
            
            # Only draw zombie and text if word is not complete
            if not self.word_complete:
                draw_texture(self.zombie_texture, self.zombie_x, 225, self.zombie_w * 1.5, self.zombie_h * 1.5)
                draw_texture(self.text_texture, self.zombie_x + 35, 200, self.tw, self.th)
            
            # Draw bullets
            for bullet in self.bullets:
                draw_rectangle(bullet['x'], bullet['y'], 15, 5, color=(1, 1, 0))  # Yellow bullets
                glColor3f(1, 1, 1)  # Reset color to white after drawing bullet

            pg.display.flip()
            self.clock.tick(60)
        
        self.quit()
    
    def quit(self):
        pg.quit()

if __name__ == "__main__":
    myApp = App()
