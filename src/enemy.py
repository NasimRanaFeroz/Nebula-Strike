try:
    import pygame
except ImportError:
    import pygame_ce as pygame
import random
import math
from src.bullet import Bullet


class Enemy:
    """Base enemy class"""
    
    def __init__(self, x, y, enemy_type="basic"):
        """Initialize enemy"""
        self.x = x
        self.y = y
        self.enemy_type = enemy_type
        self.width = 40
        self.height = 40
        
        # Set stats based on type
        self.set_stats()
        
        # Movement
        self.speed_x = 0
        self.speed_y = 2
        self.movement_pattern = "straight"
        self.pattern_timer = 0
        
        # Shooting
        self.bullets = []
        self.shoot_cooldown = 0
        self.shoot_delay = 60
        
        # Create collision rect
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height)
        
        # Load placeholder image
        self.image = None
        self.load_assets()
        
    def set_stats(self):
        """Set enemy stats based on type"""
        if self.enemy_type == "basic":
            self.max_health = 20
            self.health = self.max_health
            self.score_value = 100
            self.damage = 10
        elif self.enemy_type == "zigzag":
            self.max_health = 30
            self.health = self.max_health
            self.score_value = 200
            self.damage = 15
            self.movement_pattern = "zigzag"
        elif self.enemy_type == "elite":
            self.max_health = 50
            self.health = self.max_health
            self.score_value = 300
            self.damage = 20
            self.shoot_delay = 40
            self.movement_pattern = "sine"
        elif self.enemy_type == "kamikaze":
            self.max_health = 15
            self.health = self.max_health
            self.score_value = 150
            self.damage = 30
            self.speed_y = 4
            
    def load_assets(self):
        """Load enemy sprite"""
        import os
        basic_path = os.path.join("assets", "images", "basic-enemy.png")
        enemy2_path = os.path.join("assets", "images", "enemy-2.png")
        
        # Determine which image to use based on enemy type
        if self.enemy_type in ["basic", "kamikaze"]:
            image_path = basic_path
        else:  # zigzag, elite
            image_path = enemy2_path
        
        if os.path.exists(image_path):
            try:
                loaded_img = pygame.image.load(image_path).convert_alpha()
                self.image = pygame.transform.scale(loaded_img, (self.width, self.height))
            except:
                self._create_placeholder_image()
        else:
            self._create_placeholder_image()
    
    def _create_placeholder_image(self):
        """Create placeholder colored rectangle"""
        self.image = pygame.Surface((self.width, self.height))
        if self.enemy_type == "basic":
            self.image.fill((255, 100, 100))  # Red
        elif self.enemy_type == "zigzag":
            self.image.fill((255, 200, 100))  # Orange
        elif self.enemy_type == "elite":
            self.image.fill((200, 100, 255))  # Purple
        elif self.enemy_type == "kamikaze":
            self.image.fill((255, 50, 50))  # Dark red
            
    def update(self):
        """Update enemy position and behavior"""
        # Update movement based on pattern
        self.pattern_timer += 1
        
        if self.movement_pattern == "straight":
            self.y += self.speed_y
        elif self.movement_pattern == "zigzag":
            self.y += self.speed_y
            self.x += math.sin(self.pattern_timer * 0.1) * 3
        elif self.movement_pattern == "sine":
            self.y += self.speed_y
            self.x += math.sin(self.pattern_timer * 0.05) * 5
        elif self.movement_pattern == "circle":
            angle = self.pattern_timer * 0.05
            radius = 100
            center_x = 400
            self.x = center_x + math.cos(angle) * radius
            self.y += self.speed_y * 0.5
            
        # Update rect
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2
        
        # Shooting behavior
        if self.shoot_cooldown > 0:
            self.shoot_cooldown -= 1
        else:
            if self.enemy_type in ["elite", "zigzag"] and random.random() < 0.02:
                self.shoot()
                
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > 610 or bullet.y < -10:
                self.bullets.remove(bullet)
                
    def shoot(self):
        """Enemy fires bullets"""
        self.shoot_cooldown = self.shoot_delay
        bullet = Bullet(self.x, self.y + self.height // 2, 0, 5, "enemy")
        self.bullets.append(bullet)
        
    def take_damage(self, damage):
        """Take damage from player weapons"""
        self.health -= damage
        self.health = max(0, self.health)
        
    def draw(self, screen):
        """Draw the enemy and its bullets"""
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
        # Draw health bar for elites
        if self.enemy_type in ["elite", "boss"] and self.health < self.max_health:
            bar_width = self.width
            bar_height = 5
            bar_x = self.rect.x
            bar_y = self.rect.y - 10
            
            # Background
            pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
            # Health
            current_width = int((self.health / self.max_health) * bar_width)
            pygame.draw.rect(screen, (255, 0, 0), (bar_x, bar_y, current_width, bar_height))
            
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)


class EnemyManager:
    """Manages all enemies in the game"""
    
    def __init__(self):
        """Initialize enemy manager"""
        self.enemies = []
        self.spawn_timer = 0
        
    def spawn_enemy(self, enemy_data):
        """Spawn an enemy based on provided data"""
        x = enemy_data.get("x", random.randint(50, 750))
        y = enemy_data.get("y", -50)
        enemy_type = enemy_data.get("type", "basic")
        
        enemy = Enemy(x, y, enemy_type)
        
        # Apply any special movement patterns
        if "pattern" in enemy_data:
            enemy.movement_pattern = enemy_data["pattern"]
        if "speed_y" in enemy_data:
            enemy.speed_y = enemy_data["speed_y"]
            
        self.enemies.append(enemy)
        
    def update(self):
        """Update all enemies"""
        for enemy in self.enemies[:]:
            enemy.update()
            
            # Remove enemies that are off screen
            if enemy.y > 650:
                self.enemies.remove(enemy)
                
    def draw(self, screen):
        """Draw all enemies"""
        for enemy in self.enemies:
            enemy.draw(screen)
            
    def clear_all(self):
        """Remove all enemies"""
        self.enemies.clear()
