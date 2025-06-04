import pygame as pg
from OpenGL.GL import *
from texture import load_texture, draw_texture, draw_rectangle
from text_manager import render_text
from health_system import HealthSystem
from zombie import Zombie
from score_system import ScoreSystem
from audio_manager import AudioManager
import random

class App:
    def __init__(self):
        pg.init()
        pg.display.set_mode((640, 480), pg.OPENGL | pg.DOUBLEBUF)
        self.clock = pg.time.Clock()
        self._setup_opengl()
        self._load_textures()
        self._initialize_game_systems()
        self.mainLoop()

    def _setup_opengl(self):
        """Setup OpenGL environment"""
        glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA)
        
        glMatrixMode(GL_PROJECTION)
        glLoadIdentity()
        glOrtho(0, 640, 480, 0, -1, 1)  
        glMatrixMode(GL_MODELVIEW)

        glClearColor(0.1, 0.2, 0.2, 1)

    def _load_textures(self):
        """Load all game textures"""
        self.sky_texture, self.sky_w, self.sky_h = load_texture("assets/images/sky.png")
        self.player_texture, self.player_w, self.player_h = load_texture("assets/images/player.png")
        self.zombie_texture, self.zombie_w, self.zombie_h = load_texture("assets/images/zombie.png")
        self.ground_texture, self.ground_w, self.ground_h = load_texture("assets/images/ground.png")

    def _initialize_game_systems(self):
        """Initialize all game systems and variables"""
        # Player setup
        self.player_x = 50
        self.player_y = 225
        self.player_speed = 5
        
        # Game systems
        self.health_system = HealthSystem(max_health=100, damage_rate=20)
        self.score_system = ScoreSystem(target_score=10)
        self.audio_manager = AudioManager()  # Initialize audio manager
        
        # Zombie management
        self.zombies = []
        self.active_zombie_index = None
        self.zombie_spawn_timer = 0
        self.zombie_spawn_interval = 3
        self.zombie_words = ["zombie", "ghost", "monster", "creature", "undead", "horror", "scary", "dead"]
        
        # Bullet system
        self.bullets = []
        self.bullet_speed = 4000

    def spawn_zombie(self):
        """Spawn a new zombie with random word and speed"""
        word = random.choice(self.zombie_words)
        speed = random.uniform(50, 150)
        zombie = Zombie(
            x=640,
            y=225,
            speed=speed,
            word=word,
            zombie_texture=self.zombie_texture,
            zombie_w=self.zombie_w,
            zombie_h=self.zombie_h
        )
        self.zombies.append(zombie)

    def handle_input(self, event):
        """Handle all game input"""
        if event.type == pg.QUIT:
            return False
        
        if event.type == pg.KEYDOWN:
            if self.score_system.game_won:
                if self.score_system.handle_win_screen_input(event):
                    self.reset_game()
                return True
            elif self.score_system.game_over:
                if self.score_system.handle_game_over_input(event):
                    self.reset_game()
                return True

            typed_letter = event.unicode.lower()
            self._handle_typing(typed_letter)
        
        return True

    def _handle_typing(self, typed_letter):
        """Handle typing mechanics"""
        # Find new zombie to type if none active
        if self.active_zombie_index is None:
            for i, zombie in enumerate(self.zombies):
                if zombie.alive and zombie.word and typed_letter == zombie.word[0]:
                    self.active_zombie_index = i
                    break
        
        # Process typing for active zombie
        if self.active_zombie_index is not None:
            zombie = self.zombies[self.active_zombie_index]
            if zombie.process_typed_letter(typed_letter):
                self._fire_bullet()
                if not zombie.word:
                    zombie.alive = False
                    if self.score_system.increment_score():
                        self.score_system.game_won = True
                        print(f"Game won! Score: {self.score_system.score}")  # Debug print
                    self.active_zombie_index = None
            elif typed_letter != zombie.word[0]:
                self.active_zombie_index = None

    def _fire_bullet(self):
        """Fire a bullet at the active zombie"""
        self.bullets.append({
            'x': self.player_x + self.player_w // 2,
            'y': self.player_y + 50,
            'target_zombie': self.active_zombie_index
        })
        # Play fire sound effect
        self.audio_manager.play_sound('fire')

    def update(self, dt):
        """Update all game systems"""
        if self.score_system.game_won or self.score_system.game_over:
            return True

        # Spawn new zombies
        self.zombie_spawn_timer += dt
        if self.zombie_spawn_timer >= self.zombie_spawn_interval:
            self.spawn_zombie()
            self.zombie_spawn_timer = 0
        
        # Update zombies
        player_right_edge = self.player_x + (self.player_w * 1.5)
        is_any_zombie_close = False
        
        for zombie in self.zombies[:]:
            if zombie.alive:
                distance = zombie.update(dt, player_right_edge, -50)
                if distance <= -50:
                    is_any_zombie_close = True
            else:
                self.zombies.remove(zombie)
        
        # Update health system
        if not self.health_system.update(dt, is_any_zombie_close, False):
            self.score_system.set_game_over()
            return True
        
        # Update bullets
        self._update_bullets(dt)
        
        return True

    def _update_bullets(self, dt):
        """Update bullet positions and check collisions"""
        for bullet in self.bullets[:]:
            bullet['x'] += self.bullet_speed * dt
            
            if bullet['target_zombie'] < len(self.zombies):
                target_zombie = self.zombies[bullet['target_zombie']]
                if (target_zombie.alive and
                    bullet['x'] >= target_zombie.x and 
                    bullet['x'] <= target_zombie.x + target_zombie.zombie_w * 1.5 and
                    bullet['y'] >= target_zombie.y and 
                    bullet['y'] <= target_zombie.y + target_zombie.zombie_h * 1.5):
                    self.bullets.remove(bullet)
            elif bullet['x'] > 640:
                self.bullets.remove(bullet)

    def draw(self):
        """Draw all game elements"""
        if self.score_system.game_won:
            self.score_system.draw_win_screen()
            return
        elif self.score_system.game_over:
            self.score_system.draw_game_over_screen()
            return
            
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw background
        draw_texture(self.sky_texture, 0, 0, self.sky_w, self.sky_h)
        draw_texture(self.ground_texture, 0, 0, self.ground_w // 2, self.ground_h // 1.5)
        
        # Draw player
        draw_texture(self.player_texture, self.player_x, self.player_y, self.player_w * 1.5, self.player_h * 1.5)
        
        # Draw game systems
        self.health_system.draw()
        self.score_system.draw_score()
        
        # Draw zombies
        for zombie in self.zombies:
            if zombie.alive:
                zombie.draw()
        
        # Draw bullets
        for bullet in self.bullets:
            draw_rectangle(bullet['x'], bullet['y'], 15, 5, color=(1, 1, 0))
            glColor3f(1, 1, 1)

        pg.display.flip()

    def reset_game(self):
        """Reset the game state"""
        self.score_system.reset()
        self.zombies.clear()
        self.bullets.clear()
        self.active_zombie_index = None
        self.zombie_spawn_timer = 0
        self.health_system = HealthSystem(max_health=100, damage_rate=20)

    def mainLoop(self):
        running = True
        while running:
            # Handle events
            for event in pg.event.get():
                if not self.handle_input(event):
                    running = False
                    break
            
            # Update game state
            dt = self.clock.tick(60) / 1000
            
            # Check game state before updating
            if self.score_system.game_won:
                self.score_system.draw_win_screen()
                continue
            elif self.score_system.game_over:
                self.score_system.draw_game_over_screen()
                continue
                
            if not self.update(dt):
                running = False
                break
            
            # Draw game
            self.draw()
        
        self.quit()
    
    def quit(self):
        """Clean up resources before quitting"""
        self.audio_manager.cleanup()  # Clean up audio resources
        pg.quit()

if __name__ == "__main__":
    myApp = App()
