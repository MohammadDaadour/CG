from OpenGL.GL import *
from draw_utils import draw_rectangle, draw_circle, draw_ellipse
import math

class HealthSystem:
    def __init__(self, max_health=100, damage_rate=20):
        self.max_health = max_health
        self.current_health = max_health
        self.damage_rate = damage_rate
        self.regen_rate = 5
        
        # Health bar visual properties
        self.health_bar_width = 210
        self.health_bar_height = 20
        self.health_bar_x = 50
        self.health_bar_y = 20
        
        # Heart properties
        self.heart_size = 30
        self.heart_x = 15
        self.heart_y = 15

    def get_health_color(self):
        """Get color based on health percentage"""
        health_percent = self.current_health / self.max_health
        if health_percent > 0.6:
            return (0.2, 0.8, 0.2)  # Bright green
        elif health_percent > 0.3:
            return (0.8, 0.8, 0.2)  # Yellow
        else:
            return (0.8, 0.2, 0.2)  # Red

    def draw_simple_health_bar(self):
        """Draw a simple rectangular health bar with a border"""
        # Draw background (gray)
        draw_rectangle(
            self.health_bar_x,
            self.health_bar_y,
            self.health_bar_width,
            self.health_bar_height,
            color=(0.3, 0.3, 0.3)
        )
        # Draw current health
        health_width = (self.current_health / self.max_health) * self.health_bar_width
        if health_width > 0:
            draw_rectangle(
                self.health_bar_x,
                self.health_bar_y,
                health_width,
                self.health_bar_height,
                color=self.get_health_color()
            )
        # Draw border
        draw_rectangle(
            self.health_bar_x,
            self.health_bar_y,
            self.health_bar_width,
            self.health_bar_height,
            color=(1, 1, 1),
            filled=False
        )

    def draw_heart(self, x, y, size, color):
        """Draw a heart shape"""
        # Left side of heart
        draw_ellipse(x + size/4, y + size/4, size/4, size/4, color)
        # Right side of heart
        draw_ellipse(x + size*3/4, y + size/4, size/4, size/4, color)
        # Bottom triangle
        glColor3f(*color)
        glBegin(GL_TRIANGLES)
        glVertex2f(x + size/2, y + size)
        glVertex2f(x, y + size/4)
        glVertex2f(x + size, y + size/4)
        glEnd()

    def draw(self):
        """Draw the health bar and heart icon"""
        # Draw heart icon
        heart_color = self.get_health_color() if self.current_health > 0 else (0.5, 0.5, 0.5)
        self.draw_heart(self.heart_x, self.heart_y, self.heart_size, heart_color)
        # Draw health bar
        self.draw_simple_health_bar()
        # Reset color
        glColor3f(1, 1, 1)

    def update(self, dt, is_zombie_close, is_word_complete):
        """Update health based on game conditions. Returns True if player is still alive, False if dead."""
        if is_zombie_close and not is_word_complete:
            self.current_health -= self.damage_rate * dt
            self.current_health = max(0, self.current_health)
        elif not is_zombie_close:
            self.current_health += self.regen_rate * dt
            self.current_health = min(self.max_health, self.current_health)
        return self.current_health > 0

    def get_health_percentage(self):
        """Get current health as a percentage"""
        return (self.current_health / self.max_health) * 100

    def reset(self):
        """Reset health to maximum"""
        self.current_health = self.max_health 