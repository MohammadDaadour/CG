import pygame as pg
from OpenGL.GL import *
from texture import draw_texture, draw_rectangle
from text_manager import render_text

class ScoreSystem:
    def __init__(self, target_score=10):
        self.score = 0
        self.target_score = target_score
        self.game_won = False
        self.game_over = False
        print(f"Score system initialized with target score: {target_score}")  # Debug print

    def increment_score(self):
        """Increment score and check for win condition"""
        self.score += 1
        print(f"Score incremented to: {self.score}")  # Debug print
        if self.score >= self.target_score:
            self.game_won = True
            print(f"Win condition met! Score: {self.score}, Target: {self.target_score}")  # Debug print
        return self.game_won

    def draw_score(self):
        """Draw the score in the top right corner"""
        score_text = f"Score: {self.score}/{self.target_score}"
        score_texture, score_w, score_h = render_text(score_text)
        draw_texture(score_texture, 640 - score_w - 20, 20, score_w, score_h)
        glDeleteTextures([score_texture])

    def draw_win_screen(self):
        """Draw the win screen"""
        print("Drawing win screen")  # Debug print
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw semi-transparent black background
        draw_rectangle(0, 0, 640, 480, color=(0, 0, 0), alpha=0.7)
        
        # Draw win message
        win_text = "YOU WIN!"
        win_texture, win_w, win_h = render_text(win_text, font_size=48)  # Larger text
        draw_texture(win_texture, 320 - win_w//2, 240 - win_h//2, win_w, win_h)
        glDeleteTextures([win_texture])
        
        # Draw final score
        final_score_text = f"Final Score: {self.score}"
        score_texture, score_w, score_h = render_text(final_score_text)
        draw_texture(score_texture, 320 - score_w//2, 240 + win_h//2 + 20, score_w, score_h)
        glDeleteTextures([score_texture])
        
        # Draw restart instruction
        restart_text = "Press SPACE to restart"
        restart_texture, restart_w, restart_h = render_text(restart_text)
        draw_texture(restart_texture, 320 - restart_w//2, 240 + win_h//2 + 60, restart_w, restart_h)
        glDeleteTextures([restart_texture])
        
        pg.display.flip()

    def set_game_over(self):
        """Set game over state"""
        self.game_over = True
        print("Game Over!")  # Debug print

    def draw_game_over_screen(self):
        """Draw the game over screen"""
        print("Drawing game over screen")  # Debug print
        glClear(GL_COLOR_BUFFER_BIT)
        
        # Draw semi-transparent black background
        draw_rectangle(0, 0, 640, 480, color=(0, 0, 0), alpha=0.7)
        
        # Draw game over message
        game_over_text = "GAME OVER!"
        game_over_texture, game_over_w, game_over_h = render_text(game_over_text, font_size=48)
        draw_texture(game_over_texture, 320 - game_over_w//2, 240 - game_over_h//2, game_over_w, game_over_h)
        glDeleteTextures([game_over_texture])
        
        # Draw final score
        final_score_text = f"Final Score: {self.score}"
        score_texture, score_w, score_h = render_text(final_score_text)
        draw_texture(score_texture, 320 - score_w//2, 240 + game_over_h//2 + 20, score_w, score_h)
        glDeleteTextures([score_texture])
        
        # Draw restart instruction
        restart_text = "Press SPACE to restart"
        restart_texture, restart_w, restart_h = render_text(restart_text)
        draw_texture(restart_texture, 320 - restart_w//2, 240 + game_over_h//2 + 60, restart_w, restart_h)
        glDeleteTextures([restart_texture])
        
        pg.display.flip()

    def handle_game_over_input(self, event):
        """Handle input during game over screen"""
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            return True  # Return True to indicate restart
        return False

    def reset(self):
        """Reset the score system"""
        self.score = 0
        self.game_won = False
        self.game_over = False

    def handle_win_screen_input(self, event):
        """Handle input during win screen"""
        if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
            return True  # Return True to indicate restart
        return False 