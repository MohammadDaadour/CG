# Typing Zombie Defense Game

## Overview

Typing Zombie Defense is an educational game that combines typing practice with action gameplay. Players defend against approaching zombies by typing the words associated with them. The game features power-ups, health management, and score tracking, all implemented using computer graphics algorithms.

## Game Mechanics

### Core Gameplay

- **Objective**: Defeat zombies by typing the words displayed above them before they reach your character
- **Win Condition**: Reach the target score (default: 10 zombies defeated)
- **Lose Condition**: Health reaches zero when zombies get too close

### Player Character

- Fixed position on the left side of the screen
- Automatically fires bullets at zombies when correct letters are typed
- Has a health bar that decreases when zombies get too close
- Health regenerates when no zombies are nearby

### Zombies

- Spawn from the right side of the screen at random intervals
- Move toward the player at varying speeds
- Each zombie has a random word that must be typed to defeat it
- When a zombie's word is completely typed, it is defeated and the score increases

### Power-ups

- **Types**:
  - **Health (Green)**: Restores 30 health points
  - **Speed (Yellow)**: Increases bullet speed by 50% for 5 seconds
  - **Shield (Blue)**: Makes player invulnerable for 3 seconds
- Spawn randomly on the screen every 10 seconds
- Move toward the player after a 2-second delay
- Can be attracted to the player using the spacebar (with a 5-second cooldown)

### Visual Effects

- **Bullet Trails**: Yellow trails behind bullets using DDA line algorithm
- **Bullet Hits**: Orange expanding circles when bullets hit zombies
- **Power-up Trails**: Colored trails behind moving power-ups
- **Healing Effect**: Green crosses rotating around the player
- **Shield Effect**: Blue ellipse surrounding the player
- **Speed Boost**: Yellow lines behind the player
- **Attraction Field**: Blue pulsing circles when power-up attraction is active

## Controls

### Gameplay

- **Keyboard**: Type the letters shown above zombies to defeat them
- **Spacebar**: Activate power-up attraction (5-second cooldown)

### Game States

- **Win/Game Over Screens**: Press spacebar to restart the game

## Technical Implementation

### Graphics Algorithms

- **DDA Line Algorithm**: Used for bullet trails and attraction lines
- **Midpoint Circle Algorithm**: Used for power-ups and visual effects
- **Midpoint Ellipse Algorithm**: Used for shield effect
- **2D Transformations**: Used for rotating elements in power-ups

### Game Systems

- **Health System**: Manages player health with damage and regeneration
- **Score System**: Tracks zombie defeats and handles win/lose conditions
- **Power-up System**: Spawns and manages different types of power-ups
- **Visual Effects System**: Creates and updates various visual effects

### OpenGL Features

- Texture rendering for game elements
- Alpha blending for transparency effects
- Custom text rendering
- Point-based rendering for graphics algorithms

## User Interface

- **Health Bar**: Shows current health with color indicators (green/yellow/red)
- **Score Display**: Shows current score and target score
- **Attraction Ability**: Shows cooldown status and availability
- **Win/Game Over Screens**: Display final score and restart instructions

## Installation and Running

### Requirements

- Python 3.x
- PyGame
- PyOpenGL

### Running the Game

```
python src/main.py
```

## Credits

This game was developed as a Computer Graphics project, demonstrating various graphics algorithms and techniques in an interactive application.
