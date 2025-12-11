try:
    import pygame
except ImportError:
    import pygame_ce as pygame
from src.bullet import Bullet, HomingMissile, SpecialLaser


class Player:
    """Player spacecraft class"""
    
    def __init__(self, x, y):
        """Initialize the player"""
        self.x = x
        self.y = y
        self.width = 50
        self.height = 50
        self.speed = 5
        
        # Health system
        self.max_health = 100
        self.health = self.max_health
        
        # Weapon systems
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_delay = 10  # Frames between shots
        
        # Special weapons
        self.homing_missiles = 3
        self.special_laser_charges = 1
        
        # Power-ups and status
        self.shield_active = False
        self.shield_duration = 0
        self.weapon_level = 1  # 1-3 for different firing patterns
        
        # Create rect for collision detection
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2, 
                                self.width, self.height)
        
        # Load placeholder image (will be replaced with actual asset)
        self.image = None
        self.load_assets()
        
    def load_assets(self):
        """Load player sprite (placeholder for now)"""
        # TODO: Load actual sprite when assets are ready
        self.image = pygame.Surface((self.width, self.height))
        self.image.fill((0, 200, 255))  # Cyan placeholder
        
    def update(self):
        """Update player state"""
        # Handle keyboard input for movement
        keys = pygame.key.get_pressed()
        
        # Four-directional movement
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.y -= self.speed
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.y += self.speed
            
        # Keep player on screen
        self.x = max(self.width // 2, min(800 - self.width // 2, self.x))
        self.y = max(self.height // 2, min(600 - self.height // 2, self.y))
        
        # Update rect position
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2
        
        # Update shoot cooldown
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
            
        # Auto-fire if space is held
        if keys[pygame.K_SPACE] and self.shoot_cooldown == 0:
            self.shoot()
            
        # Update shield duration
        if self.shield_active:
            self.shield_duration -= 1
            if self.shield_duration <= 0:
                self.shield_active = False
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            # Remove bullets that are off screen
            if bullet.y < -10 or bullet.y > 610:
                self.bullets.remove(bullet)
                
    def shoot(self):
        """Fire player weapons based on weapon level"""
        if self.shoot_cooldown > 0:
            return
            
        self.shoot_cooldown = self.shoot_delay
        
        if self.weapon_level == 1:
            # Single shot
            bullet = Bullet(self.x, self.y - self.height // 2, 0, -10, "player")
            self.bullets.append(bullet)
        elif self.weapon_level == 2:
            # Double shot
            bullet1 = Bullet(self.x - 15, self.y - self.height // 2, 0, -10, "player")
            bullet2 = Bullet(self.x + 15, self.y - self.height // 2, 0, -10, "player")
            self.bullets.extend([bullet1, bullet2])
        elif self.weapon_level >= 3:
            # Triple shot with spread
            bullet1 = Bullet(self.x, self.y - self.height // 2, 0, -10, "player")
            bullet2 = Bullet(self.x - 15, self.y - self.height // 2, -2, -10, "player")
            bullet3 = Bullet(self.x + 15, self.y - self.height // 2, 2, -10, "player")
            self.bullets.extend([bullet1, bullet2, bullet3])
            
    def fire_homing_missile(self, target=None):
        """Fire a homing missile at a target"""
        if self.homing_missiles > 0:
            missile = HomingMissile(self.x, self.y, target)
            self.bullets.append(missile)
            self.homing_missiles -= 1
            
    def use_special_weapon(self):
        """Activate special laser weapon"""
        if self.special_laser_charges > 0:
            laser = SpecialLaser(self.x, self.y)
            self.bullets.append(laser)
            self.special_laser_charges -= 1
            
    def take_damage(self, damage):
        """Take damage if not shielded"""
        if not self.shield_active:
            self.health -= damage
            self.health = max(0, self.health)
            
    def heal(self, amount):
        """Restore health"""
        self.health = min(self.max_health, self.health + amount)
        
    def activate_shield(self, duration=300):
        """Activate shield for specified duration (frames)"""
        self.shield_active = True
        self.shield_duration = duration
        
    def is_shielded(self):
        """Check if shield is active"""
        return self.shield_active
        
    def upgrade_weapon(self):
        """Upgrade weapon level"""
        self.weapon_level = min(3, self.weapon_level + 1)
        
    def apply_powerup(self, powerup):
        """Apply a collected power-up"""
        if powerup.type == "health":
            self.heal(30)
        elif powerup.type == "shield":
            self.activate_shield(300)
        elif powerup.type == "weapon_upgrade":
            self.upgrade_weapon()
        elif powerup.type == "missiles":
            self.homing_missiles += 3
        elif powerup.type == "special_laser":
            self.special_laser_charges += 1
            
    def draw(self, screen):
        """Draw the player and its bullets"""
        # Draw player ship
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
        # Draw shield effect if active
        if self.shield_active:
            pygame.draw.circle(screen, (100, 200, 255), (int(self.x), int(self.y)), 
                             self.width // 2 + 10, 3)
                             
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
