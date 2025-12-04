import pygame
import math


class Bullet:
    """Basic bullet class for both player and enemies"""
    
    def __init__(self, x, y, speed_x, speed_y, owner="player"):
        """Initialize bullet"""
        self.x = x
        self.y = y
        self.speed_x = speed_x
        self.speed_y = speed_y
        self.owner = owner  # "player" or "enemy"
        self.width = 5
        self.height = 15
        self.damage = 10
        
        # Create collision rect
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height)
        
        # Color based on owner
        if owner == "player":
            self.color = (100, 255, 100)  # Green
        else:
            self.color = (255, 100, 100)  # Red
            
    def update(self):
        """Update bullet position"""
        self.x += self.speed_x
        self.y += self.speed_y
        
        # Update rect
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2
        
    def draw(self, screen):
        """Draw the bullet"""
        pygame.draw.rect(screen, self.color, self.rect)
        # Add glow effect
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 1)


class HomingMissile(Bullet):
    """Homing missile that tracks enemies"""
    
    def __init__(self, x, y, target=None):
        """Initialize homing missile"""
        super().__init__(x, y, 0, -8, "player")
        self.target = target
        self.width = 8
        self.height = 20
        self.damage = 30
        self.color = (255, 200, 0)  # Gold
        self.homing_strength = 0.3
        self.max_turn_rate = 5
        
    def update(self):
        """Update missile with homing behavior"""
        # If we have a target and it's still alive, home in on it
        if self.target and hasattr(self.target, 'health') and self.target.health > 0:
            # Calculate direction to target
            dx = self.target.x - self.x
            dy = self.target.y - self.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance > 0:
                # Normalize and apply homing
                dx /= distance
                dy /= distance
                
                # Adjust velocity towards target
                self.speed_x += dx * self.homing_strength
                self.speed_y += dy * self.homing_strength
                
                # Limit turn rate
                speed = math.sqrt(self.speed_x**2 + self.speed_y**2)
                if speed > 10:
                    self.speed_x = (self.speed_x / speed) * 10
                    self.speed_y = (self.speed_y / speed) * 10
        
        # Update position
        super().update()
        
    def draw(self, screen):
        """Draw the homing missile with trail effect"""
        # Draw main missile
        pygame.draw.rect(screen, self.color, self.rect)
        # Draw trail
        trail_length = 10
        pygame.draw.line(screen, (255, 150, 0), 
                        (int(self.x), int(self.y)),
                        (int(self.x - self.speed_x), int(self.y - self.speed_y)), 3)


class SpecialLaser:
    """Special laser weapon that clears the screen"""
    
    def __init__(self, x, y):
        """Initialize special laser"""
        self.x = x
        self.y = y
        self.width = 30
        self.height = 600  # Full screen height
        self.damage = 100
        self.duration = 30  # Frames the laser lasts
        self.timer = 0
        
        # Create collision rect
        self.rect = pygame.Rect(self.x - self.width // 2, 0, self.width, self.height)
        
    def update(self):
        """Update laser duration"""
        self.timer += 1
        
    def is_finished(self):
        """Check if laser animation is complete"""
        return self.timer >= self.duration
        
    def draw(self, screen):
        """Draw the special laser with effects"""
        if self.timer < self.duration:
            alpha = max(0, 255 - (self.timer * 8))
            
            # Create laser surface with transparency
            laser_surf = pygame.Surface((self.width, self.height))
            laser_surf.set_alpha(alpha)
            laser_surf.fill((100, 200, 255))
            
            # Draw laser
            screen.blit(laser_surf, (self.x - self.width // 2, 0))
            
            # Draw outer glow
            glow_width = self.width + 10
            glow_surf = pygame.Surface((glow_width, self.height))
            glow_surf.set_alpha(alpha // 2)
            glow_surf.fill((200, 230, 255))
            screen.blit(glow_surf, (self.x - glow_width // 2, 0))


class BossBullet(Bullet):
    """Special bullet type for boss attacks"""
    
    def __init__(self, x, y, speed_x, speed_y, pattern="normal"):
        """Initialize boss bullet"""
        super().__init__(x, y, speed_x, speed_y, "enemy")
        self.pattern = pattern
        self.width = 10
        self.height = 10
        self.damage = 20
        self.timer = 0
        self.color = (255, 0, 255)  # Magenta
        
    def update(self):
        """Update boss bullet with special patterns"""
        self.timer += 1
        
        if self.pattern == "spiral":
            # Spiral pattern
            angle = self.timer * 0.1
            self.speed_x = math.cos(angle) * 3
            self.speed_y += 0.1
        elif self.pattern == "accelerate":
            # Accelerating bullet
            self.speed_y += 0.2
        elif self.pattern == "wave":
            # Wave pattern
            self.x += math.sin(self.timer * 0.1) * 2
            
        super().update()
        
    def draw(self, screen):
        """Draw boss bullet with special effects"""
        pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), 
                          self.width // 2)
        # Outer ring
        pygame.draw.circle(screen, (255, 255, 255), (int(self.x), int(self.y)), 
                          self.width // 2, 2)
