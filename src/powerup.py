import pygame
import random


class PowerUp:
    """Power-up collectible class"""
    
    def __init__(self, x, y, powerup_type):
        """Initialize power-up"""
        self.x = x
        self.y = y
        self.type = powerup_type
        self.width = 30
        self.height = 30
        self.speed_y = 2
        
        # Create collision rect
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height)
        
        # Visual properties
        self.color = self.get_color()
        self.image = None
        self.load_assets()
        
        # Animation
        self.pulse_timer = 0
        
    def get_color(self):
        """Get color based on power-up type"""
        colors = {
            "health": (0, 255, 0),         # Green
            "shield": (0, 200, 255),       # Cyan
            "weapon_upgrade": (255, 200, 0), # Gold
            "missiles": (255, 100, 0),     # Orange
            "special_laser": (200, 0, 255), # Purple
            "speed": (255, 255, 0),        # Yellow
            "score": (255, 255, 255)       # White
        }
        return colors.get(self.type, (255, 255, 255))
        
    def load_assets(self):
        """Load power-up sprite (placeholder)"""
        # TODO: Load actual sprites when assets are ready
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill(self.color)
        
    def update(self):
        """Update power-up position and animation"""
        self.y += self.speed_y
        self.pulse_timer += 1
        
        # Update rect
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2
        
    def draw(self, screen):
        """Draw the power-up with pulsing effect"""
        # Pulsing animation
        pulse = abs(math.sin(self.pulse_timer * 0.1))
        size_mod = int(5 * pulse)
        
        # Draw outer glow
        glow_rect = pygame.Rect(
            self.rect.x - size_mod,
            self.rect.y - size_mod,
            self.width + size_mod * 2,
            self.height + size_mod * 2
        )
        glow_surf = pygame.Surface((glow_rect.width, glow_rect.height))
        glow_surf.set_alpha(100)
        glow_surf.fill(self.color)
        screen.blit(glow_surf, (glow_rect.x, glow_rect.y))
        
        # Draw main power-up
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
        # Draw icon/symbol (placeholder)
        font = pygame.font.Font(None, 20)
        symbols = {
            "health": "H",
            "shield": "S",
            "weapon_upgrade": "W",
            "missiles": "M",
            "special_laser": "L",
            "speed": ">>",
            "score": "$"
        }
        symbol = symbols.get(self.type, "?")
        text = font.render(symbol, True, (0, 0, 0))
        screen.blit(text, (self.rect.x + self.width // 2 - text.get_width() // 2,
                          self.rect.y + self.height // 2 - text.get_height() // 2))


import math


class PowerUpManager:
    """Manages all power-ups in the game"""
    
    def __init__(self):
        """Initialize power-up manager"""
        self.powerups = []
        self.spawn_chance = 0.15  # 15% chance to drop from enemies
        
        # Power-up drop weights (higher = more common)
        self.drop_weights = {
            "health": 30,
            "shield": 20,
            "weapon_upgrade": 15,
            "missiles": 20,
            "special_laser": 10,
            "speed": 5,
            "score": 25
        }
        
    def try_spawn(self, x, y):
        """Attempt to spawn a power-up at the given position"""
        if random.random() < self.spawn_chance:
            powerup_type = self.weighted_random_choice()
            powerup = PowerUp(x, y, powerup_type)
            self.powerups.append(powerup)
            
    def weighted_random_choice(self):
        """Choose a power-up type based on weights"""
        total_weight = sum(self.drop_weights.values())
        rand_val = random.uniform(0, total_weight)
        
        current_weight = 0
        for powerup_type, weight in self.drop_weights.items():
            current_weight += weight
            if rand_val <= current_weight:
                return powerup_type
                
        return "health"  # Fallback
        
    def spawn_powerup(self, x, y, powerup_type):
        """Spawn a specific power-up (for scripted events)"""
        powerup = PowerUp(x, y, powerup_type)
        self.powerups.append(powerup)
        
    def update(self):
        """Update all power-ups"""
        for powerup in self.powerups[:]:
            powerup.update()
            
            # Remove power-ups that are off screen
            if powerup.y > 650:
                self.powerups.remove(powerup)
                
    def draw(self, screen):
        """Draw all power-ups"""
        for powerup in self.powerups:
            powerup.draw(screen)
            
    def clear_all(self):
        """Remove all power-ups"""
        self.powerups.clear()
