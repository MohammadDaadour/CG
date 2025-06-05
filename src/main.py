import pygame as pg
from OpenGL.GL import *
from texture import load_texture, draw_texture, draw_rectangle
from text_manager import render_text
from health_system import HealthSystem
from zombie import Zombie
from score_system import ScoreSystem
from graphics_algorithms import dda_line, midpoint_circle, midpoint_ellipse, clip_line, rotate_point, translate_point, scale_point
from audio_manager import AudioManager
import random
import math

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
        self.bullet_trails = []
        
        # Power-up system using midpoint circle algorithm
        self.powerups = []
        self.powerup_spawn_timer = 0
        self.powerup_spawn_interval = 10  # Spawn every 10 seconds
        self.powerup_types = ["health", "speed", "shield"]
        self.attract_powerups = False  # Flag for powerup attraction
        self.attract_cooldown = 0  # Cooldown for attraction ability
        
        # Visual effects
        self.visual_effects = []

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

            # Attract powerups with spacebar if cooldown is ready
            if event.key == pg.K_SPACE and self.attract_cooldown <= 0:
                self.attract_powerups = True
                self.attract_cooldown = 5  # 5 second cooldown
                # Add visual effect to show attraction is active
                self._add_visual_effect("attract", self.player_x + self.player_w * 0.75, 
                                       self.player_y + self.player_h * 0.75, 
                                       duration=1.0, radius=100, 
                                       color=(0.8, 0.8, 1.0, 0.5))
                return True

            typed_letter = event.unicode.lower()
            self._handle_typing(typed_letter)
        
        # Handle custom events for powerup timeouts
        if event.type == pg.USEREVENT + 1:  # Speed powerup timeout
            self.bullet_speed /= 1.5  # Reset bullet speed
            pg.time.set_timer(pg.USEREVENT + 1, 0)  # Disable timer
        
        if event.type == pg.USEREVENT + 2:  # Shield powerup timeout
            self.health_system.damage_rate = 20  # Reset damage rate
            pg.time.set_timer(pg.USEREVENT + 2, 0)  # Disable timer
        
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
        start_x = self.player_x + self.player_w // 2
        start_y = self.player_y + 50
        
        # Get target zombie position for trajectory
        if self.active_zombie_index is not None and self.active_zombie_index < len(self.zombies):
            target_zombie = self.zombies[self.active_zombie_index]
            target_x = target_zombie.x + target_zombie.zombie_w // 2
            target_y = target_zombie.y + target_zombie.zombie_h // 2
        else:
            # Default trajectory if no target
            target_x = start_x + 100
            target_y = start_y
        
        # Calculate angle for visual effect
        angle = math.atan2(target_y - start_y, target_x - start_x)
        
        self.bullets.append({
            'x': start_x,
            'y': start_y,
            'target_zombie': self.active_zombie_index,
            'start_x': start_x,
            'start_y': start_y,
            'angle': angle
        })
        # Play fire sound effect
        self.audio_manager.play_sound('fire')

    def update(self, dt):
        """Update all game systems"""
        if self.score_system.game_won or self.score_system.game_over:
            return True

        # Update attract cooldown
        if self.attract_cooldown > 0:
            self.attract_cooldown -= dt
            if self.attract_cooldown <= 0:
                self.attract_powerups = False

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
        
        # Update powerups
        self._update_powerups(dt)
        
        # Update visual effects
        self._update_visual_effects(dt)
        
        return True
        
    def _update_powerups(self, dt):
        """Update and spawn powerups using midpoint circle algorithm"""
        # Spawn new powerups
        self.powerup_spawn_timer += dt
        if self.powerup_spawn_timer >= self.powerup_spawn_interval:
            # Spawn in a random position on screen
            x = random.randint(100, 540)
            y = random.randint(100, 380)
            powerup_type = random.choice(self.powerup_types)
            self.powerups.append({
                'x': x,
                'y': y,
                'type': powerup_type,
                'radius': 15,
                'active': True,
                'rotation': 0,
                'pulse': 0,
                'move_timer': 0,
                'move_speed': random.uniform(30, 60)  # Random movement speed
            })
            self.powerup_spawn_timer = 0
        
        # Update existing powerups
        for powerup in self.powerups[:]:
            # Animate powerups with rotation and pulsing
            powerup['rotation'] = (powerup['rotation'] + 90 * dt) % 360
            powerup['pulse'] = math.sin(pg.time.get_ticks() / 200) * 3
            
            # Calculate direction to player
            player_center_x = self.player_x + self.player_w * 0.75
            player_center_y = self.player_y + self.player_h * 0.75
            dx = player_center_x - powerup['x']
            dy = player_center_y - powerup['y']
            distance = math.sqrt(dx*dx + dy*dy)
            
            # Move powerups toward player
            if self.attract_powerups:
                # Fast attraction when space is pressed
                if distance > 0:
                    dx /= distance
                    dy /= distance
                    # Faster movement during attraction
                    powerup['x'] += dx * powerup['move_speed'] * 3 * dt
                    powerup['y'] += dy * powerup['move_speed'] * 3 * dt
                    
                    # Add more frequent trail effect during attraction
                    if random.random() < 0.3:  # More frequent trails
                        color = (0.0, 1.0, 0.0) if powerup['type'] == "health" else \
                                (1.0, 1.0, 0.0) if powerup['type'] == "speed" else \
                                (0.0, 0.5, 1.0)  # Shield
                        self._add_visual_effect("powerup_trail", powerup['x'], powerup['y'], 
                                               duration=0.3, radius=5, color=color)
            else:
                # Normal gradual movement
                powerup['move_timer'] += dt
                if powerup['move_timer'] > 2.0:  # Start moving after 2 seconds
                    # Normalize and apply movement
                    if distance > 0:
                        dx /= distance
                        dy /= distance
                        powerup['x'] += dx * powerup['move_speed'] * dt
                        powerup['y'] += dy * powerup['move_speed'] * dt
                        
                        # Add trail effect using midpoint circle
                        if random.random() < 0.1:  # Only add trail occasionally
                            color = (0.0, 1.0, 0.0) if powerup['type'] == "health" else \
                                    (1.0, 1.0, 0.0) if powerup['type'] == "speed" else \
                                    (0.0, 0.5, 1.0)  # Shield
                            self._add_visual_effect("powerup_trail", powerup['x'], powerup['y'], 
                                                   duration=0.3, radius=5, color=color)
            
            # Check for player collision
            player_center_x = self.player_x + self.player_w * 0.75
            player_center_y = self.player_y + self.player_h * 0.75
            distance = math.sqrt((powerup['x'] - player_center_x)**2 + (powerup['y'] - player_center_y)**2)
            
            if distance < powerup['radius'] + 30:  # Player collision radius
                self._apply_powerup(powerup['type'])
                self.powerups.remove(powerup)
    
    def _apply_powerup(self, powerup_type):
        """Apply powerup effects"""
        if powerup_type == "health":
            self.health_system.current_health = min(self.health_system.current_health + 30, self.health_system.max_health)
            # Add healing visual effect
            self._add_visual_effect("healing", self.player_x, self.player_y, duration=1.0)
        elif powerup_type == "speed":
            # Increase bullet speed temporarily
            self.bullet_speed *= 1.5
            # Schedule speed reset after 5 seconds
            pg.time.set_timer(pg.USEREVENT + 1, 5000)  # Reset in 5 seconds
            # Add speed boost visual effect
            self._add_visual_effect("speed_boost", self.player_x, self.player_y, duration=5.0)
        elif powerup_type == "shield":
            # Make player temporarily invulnerable
            self.health_system.damage_rate = 0
            # Schedule shield reset after 3 seconds
            pg.time.set_timer(pg.USEREVENT + 2, 3000)  # Reset in 3 seconds
            # Add shield visual effect
            self._add_visual_effect("shield", self.player_x, self.player_y, duration=3.0)
    
    def _update_visual_effects(self, dt):
        """Update visual effects"""
        for effect in self.visual_effects[:]:
            effect['time_left'] -= dt
            if effect['time_left'] <= 0:
                self.visual_effects.remove(effect)
            else:
                # Update effect properties based on time left
                effect['alpha'] = min(1.0, effect['time_left'])
                if effect['type'] == "bullet_hit":
                    effect['radius'] += 30 * dt  # Expand effect

    def _update_bullets(self, dt):
        """Update bullet positions and check collisions using DDA line algorithm for trails"""
        for bullet in self.bullets[:]:
            # Store previous position for trail
            prev_x, prev_y = bullet['x'], bullet['y']
            
            # Update bullet position
            bullet['x'] += self.bullet_speed * dt
            
            # Add bullet trail using DDA line algorithm
            self.bullet_trails.append({
                'start_x': prev_x,
                'start_y': prev_y,
                'end_x': bullet['x'],
                'end_y': bullet['y'],
                'time_left': 0.2,  # Trail lasts for 0.2 seconds
                'color': (1.0, 1.0, 0.0)  # Yellow trail
            })
            
            # Check for collision with zombies
            if bullet['target_zombie'] < len(self.zombies):
                target_zombie = self.zombies[bullet['target_zombie']]
                if (target_zombie.alive and
                    bullet['x'] >= target_zombie.x and 
                    bullet['x'] <= target_zombie.x + target_zombie.zombie_w * 1.5 and
                    bullet['y'] >= target_zombie.y and 
                    bullet['y'] <= target_zombie.y + target_zombie.zombie_h * 1.5):
                    # Add hit visual effect using midpoint circle
                    self._add_visual_effect("bullet_hit", target_zombie.x + target_zombie.zombie_w * 0.75, 
                                           target_zombie.y + target_zombie.zombie_h * 0.75, duration=0.3)
                    self.bullets.remove(bullet)
            elif bullet['x'] > 640:
                self.bullets.remove(bullet)
        
        # Update bullet trails
        for trail in self.bullet_trails[:]:
            trail['time_left'] -= dt
            if trail['time_left'] <= 0:
                self.bullet_trails.remove(trail)
    
    def _add_visual_effect(self, effect_type, x, y, duration=1.0, radius=None, color=None):
        """Add a visual effect at the specified position"""
        # Set default radius based on effect type if not provided
        if radius is None:
            radius = 10 if effect_type == "bullet_hit" else \
                    5 if effect_type == "powerup_trail" else 30
        
        # Set default color based on effect type if not provided
        if color is None:
            color = (1.0, 0.5, 0.0) if effect_type == "bullet_hit" else \
                   (0.0, 1.0, 0.0) if effect_type == "healing" else \
                   (0.0, 0.5, 1.0) if effect_type == "shield" else \
                   (1.0, 1.0, 0.0)  # Default yellow for speed_boost
        
        self.visual_effects.append({
            'type': effect_type,
            'x': x,
            'y': y,
            'time_left': duration,
            'alpha': 1.0,
            'radius': radius,
            'color': color
        })

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
        
        # Draw attract ability cooldown indicator
        if self.attract_cooldown > 0:
            # Draw cooldown bar
            cooldown_width = 100 * (self.attract_cooldown / 5.0)  # 5.0 is the max cooldown time
            draw_rectangle(20, 460, cooldown_width, 10, color=(0.5, 0.5, 1.0))
            
            # Draw outline (using GL_LINE_LOOP instead of filled=False)
            glColor3f(0.8, 0.8, 1.0)
            glBegin(GL_LINE_LOOP)
            glVertex2f(20, 460)
            glVertex2f(20 + 100, 460)
            glVertex2f(20 + 100, 460 + 10)
            glVertex2f(20, 460 + 10)
            glEnd()
            glColor3f(1, 1, 1)  # Reset color to white
            
            # Draw text
            cooldown_text = "ATTRACT: " + str(int(self.attract_cooldown)) + "s"
            cooldown_texture, cooldown_w, cooldown_h = render_text(cooldown_text, font_size=12, color=(255, 255, 255))
            draw_texture(cooldown_texture, 125, 460, cooldown_w, cooldown_h)
            glDeleteTextures([cooldown_texture])
        else:
            # Draw ready indicator
            draw_rectangle(20, 460, 100, 10, color=(0.8, 0.8, 1.0))
            ready_text = "ATTRACT: READY (SPACE)"
            ready_texture, ready_w, ready_h = render_text(ready_text, font_size=12, color=(255, 255, 255))
            draw_texture(ready_texture, 125, 460, ready_w, ready_h)
            glDeleteTextures([ready_texture])
        
        # Draw bullet trails using DDA line algorithm
        for trail in self.bullet_trails:
            alpha = trail['time_left'] * 5  # Fade out effect
            color = (trail['color'][0], trail['color'][1], trail['color'][2], alpha)
            dda_line(trail['start_x'], trail['start_y'], trail['end_x'], trail['end_y'], color)
        
        # Draw bullets
        for bullet in self.bullets:
            draw_rectangle(bullet['x'], bullet['y'], 15, 5, color=(1, 1, 0))
        
        # Draw zombies
        for zombie in self.zombies:
            if zombie.alive:
                zombie.draw()
        
        # Draw powerups using midpoint circle algorithm
        for powerup in self.powerups:
            # Determine color based on powerup type
            if powerup['type'] == "health":
                color = (0.0, 1.0, 0.0)  # Green for health
            elif powerup['type'] == "speed":
                color = (1.0, 1.0, 0.0)  # Yellow for speed
            else:  # Shield
                color = (0.0, 0.5, 1.0)  # Blue for shield
            
            # Draw outer circle with pulsing effect
            radius = powerup['radius'] + powerup['pulse']
            midpoint_circle(powerup['x'], powerup['y'], radius, color)
            
            # Draw inner circle
            midpoint_circle(powerup['x'], powerup['y'], radius * 0.6, (1.0, 1.0, 1.0))
            
            # Draw rotating elements using 2D transformation
            for i in range(4):
                angle = powerup['rotation'] + (i * 90)
                x, y = rotate_point(powerup['x'] + radius, powerup['y'], 
                                   powerup['x'], powerup['y'], angle)
                midpoint_circle(x, y, 3, color)
        
        # Draw visual effects
        for effect in self.visual_effects:
            if effect['type'] == "bullet_hit":
                # Draw expanding circle for bullet hit
                midpoint_circle(effect['x'], effect['y'], effect['radius'], 
                              (effect['color'][0], effect['color'][1], effect['color'][2], effect['alpha']))
            elif effect['type'] == "powerup_trail":
                # Draw fading trail for powerups
                midpoint_circle(effect['x'], effect['y'], effect['radius'] * effect['alpha'], 
                              (effect['color'][0], effect['color'][1], effect['color'][2], effect['alpha']))
            elif effect['type'] == "attract":
                # Draw attraction field effect (pulsing circle)
                # Draw multiple concentric circles with varying opacity
                for i in range(3):
                    pulse_radius = effect['radius'] * (1 - i * 0.2) * (0.8 + 0.2 * math.sin(pg.time.get_ticks() / 100))
                    alpha = effect['alpha'] * (1 - i * 0.3)
                    midpoint_circle(effect['x'], effect['y'], pulse_radius, 
                                  (effect['color'][0], effect['color'][1], effect['color'][2], alpha))
                
                # Draw lines from powerups to player when attraction is active
                if self.attract_cooldown > 0 and self.attract_powerups:
                    player_center_x = self.player_x + self.player_w * 0.75
                    player_center_y = self.player_y + self.player_h * 0.75
                    for powerup in self.powerups:
                        dda_line(powerup['x'], powerup['y'], player_center_x, player_center_y, 
                               (0.8, 0.8, 1.0, 0.3))
            elif effect['type'] == "healing":
                # Draw healing effect (green crosses)
                for i in range(8):
                    angle = (pg.time.get_ticks() / 10 + i * 45) % 360
                    x, y = rotate_point(self.player_x + 50, self.player_y + 50, 
                                       self.player_x + self.player_w * 0.75, 
                                       self.player_y + self.player_h * 0.75, angle)
                    midpoint_circle(x, y, 5, (0.0, 1.0, 0.0, effect['alpha']))
            elif effect['type'] == "shield":
                # Draw shield effect (blue circle around player)
                midpoint_ellipse(self.player_x + self.player_w * 0.75, 
                               self.player_y + self.player_h * 0.75,
                               self.player_w, self.player_h, 
                               (0.0, 0.5, 1.0, effect['alpha']))
            elif effect['type'] == "speed_boost":
                # Draw speed lines behind player
                for i in range(5):
                    start_x = self.player_x - 10 - i * 5
                    start_y = self.player_y + 20 + i * 10
                    end_x = self.player_x - 30 - i * 10
                    end_y = start_y
                    dda_line(start_x, start_y, end_x, end_y, 
                           (1.0, 1.0, 0.0, effect['alpha']))
        
        # Reset color
        glColor3f(1, 1, 1)

        pg.display.flip()

    def reset_game(self):
        """Reset the game state"""
        self.score_system.reset()
        self.zombies.clear()
        self.bullets.clear()
        self.bullet_trails.clear()
        self.powerups.clear()
        self.visual_effects.clear()
        self.active_zombie_index = None
        self.zombie_spawn_timer = 0
        self.powerup_spawn_timer = 0
        self.attract_powerups = False
        self.attract_cooldown = 0
        self.health_system = HealthSystem(max_health=100, damage_rate=20)
        self.bullet_speed = 4000  # Reset bullet speed

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
