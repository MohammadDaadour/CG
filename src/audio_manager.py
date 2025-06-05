import pygame as pg
import os
from pathlib import Path

class AudioManager:
    def __init__(self):
        # Set volume (0.0 to 1.0) - Move this before loading sounds
        self.volume = 0.5
        
        # Initialize pygame mixer with specific settings
        try:
            pg.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            print("Pygame mixer initialized successfully")
        except Exception as e:
            print(f"Error initializing pygame mixer: {e}")
            return
            
        # Load sound effects
        self.sounds = {}
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all game sound effects"""
        try:
            # Get the project root directory (assuming src folder is one level down from project root)
            current_file = Path(__file__)
            project_root = current_file.parent.parent
            sound_dir = project_root / "assets" / "sounds"
            
            # Construct the proper path for the fire sound
            fire_sound_path = sound_dir / "fire.mp3"
            
            print(f"Looking for sound file at: {fire_sound_path}")
            
            # Check if file exists
            if not fire_sound_path.exists():
                print(f"Error: Sound file does not exist at path: {fire_sound_path}")
                self.sounds['fire'] = None
                return
                
            print(f"Attempting to load sound from: {fire_sound_path}")
            self.sounds['fire'] = pg.mixer.Sound(str(fire_sound_path))
            
            # Verify sound was loaded and set volume
            if self.sounds['fire']:
                print("Successfully loaded fire sound")
                self.sounds['fire'].set_volume(self.volume)
                print(f"Sound volume set to: {self.volume}")
                
                # Test play the sound
                try:
                    self.sounds['fire'].play()
                    print("Test play of fire sound successful")
                except Exception as e:
                    print(f"Error during test play: {e}")
            else:
                print("Error: Sound object is None after loading")
                
        except Exception as e:
            print(f"Detailed error loading sounds: {str(e)}")
            print(f"Error type: {type(e).__name__}")
            self.sounds['fire'] = None
    
    def play_sound(self, sound_name):
        """Play a sound effect by name"""
        if sound_name in self.sounds:
            if self.sounds[sound_name] is None:
                print(f"Warning: Sound '{sound_name}' is None")
                return
                
            try:
                print(f"Attempting to play sound: {sound_name}")
                self.sounds[sound_name].play()
                print(f"Successfully played sound: {sound_name}")
            except Exception as e:
                print(f"Detailed error playing sound {sound_name}: {str(e)}")
                print(f"Error type: {type(e).__name__}")
        else:
            print(f"Warning: Sound '{sound_name}' not found in sounds dictionary")
    
    def set_volume(self, volume):
        """Set volume for all sounds (0.0 to 1.0)"""
        self.volume = max(0.0, min(1.0, volume))
        for sound in self.sounds.values():
            if sound:
                sound.set_volume(self.volume)
    
    def cleanup(self):
        """Clean up audio resources"""
        pg.mixer.quit()
