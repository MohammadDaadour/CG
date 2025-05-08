import pygame as pg
from OpenGL.GL import *
from texture import load_texture, draw_texture

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

        self.mainLoop()
        
    def mainLoop(self):
        running = True
        while running:
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    running = False
                    
                    
            dt = self.clock.tick(60) / 1000
            
            self.zombie_x -= self.zombie_speed * dt        

            glClear(GL_COLOR_BUFFER_BIT)
            draw_texture(self.sky_texture, 0, 0, self.sky_w, self.sky_h)
            draw_texture(self.ground_texture, 0, 0, self.ground_w // 2, self.ground_h // 1.5)
            draw_texture(self.player_texture, self.player_x, self.player_y, self.player_w * 1.5, self.player_h * 1.5)
            draw_texture(self.zombie_texture, self.zombie_x, 225, self.zombie_w * 1.5, self.zombie_h * 1.5)

            pg.display.flip()
            self.clock.tick(60)
        
        self.quit()
    
    def quit(self):
        pg.quit()

if __name__ == "__main__":
    myApp = App()
