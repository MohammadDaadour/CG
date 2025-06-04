import pygame as pg
from OpenGL.GL import *
from texture import load_texture, draw_texture

class Animation:
    def _init_(self, frame_paths, frame_time=0.1, scale=1.0):
        """
        Initialize an animation with a list of frame paths
        frame_paths: list of paths to frame images
        frame_time: time per frame in seconds
        scale: scale factor for the frames
        """
        self.frames = []
        for path in frame_paths:
            frame, w, h = load_texture(path)
            self.frames.append({
                'texture': frame,
                'width': w * scale,
                'height': h * scale
            })
        self.frame_time = frame_time
        self.current_frame = 0
        self.start_time = 0
        self.is_playing = False
        self.loop = True

    def start(self, current_time, loop=True):
        """Start playing the animation"""
        self.is_playing = True
        self.start_time = current_time
        self.current_frame = 0
        self.loop = loop

    def stop(self):
        """Stop the animation"""
        self.is_playing = False

    def update(self, current_time):
        """Update the animation state"""
        if not self.is_playing:
            return False

        if current_time - self.start_time >= self.frame_time:
            self.current_frame += 1
            self.start_time = current_time
            
            if self.current_frame >= len(self.frames):
                if self.loop:
                    self.current_frame = 0
                else:
                    self.is_playing = False
                    return True  # Animation finished
        return False

    def draw(self, x, y):
        """Draw the current frame"""
        if not self.is_playing:
            return

        frame = self.frames[self.current_frame]
        draw_texture(
            frame['texture'],
            x - frame['width'] // 2,
            y - frame['height'] // 2,
            frame['width'],
            frame['height']
        )

class AnimationManager:
    def _init_(self):
        """Initialize the animation manager"""
        self.animations = []

    def create_explosion(self, x, y, current_time, frame_paths, frame_time=0.1, scale=1.0):
        """Create a new explosion animation"""
        animation = Animation(frame_paths, frame_time, scale)
        animation.start(current_time, loop=False)
        self.animations.append({
            'animation': animation,
            'x': x,
            'y': y
        })

    def update(self, current_time):
        """Update all animations"""
        for anim_data in self.animations[:]:
            if anim_data['animation'].update(current_time):
                self.animations.remove(anim_data)

    def draw(self):
        """Draw all active animations"""
        for anim_data in self.animations:
            anim_data['animation'].draw(anim_data['x'], anim_data['y'])

    def clear(self):
        """Clear all animations"""
        self.animations.clear()