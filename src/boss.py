try:
    import pygame
except ImportError:
    import pygame_ce as pygame
import math
import random
from src.bullet import BossBullet, Bullet


class Boss:
    """Base boss class"""
    
    def __init__(self, x, y, boss_type="mini"):
        """Initialize boss"""
        self.x = x
        self.y = y
        self.boss_type = boss_type
        self.width = 100
        self.height = 100
        
        # Boss stats
        self.set_stats()
        
        # Movement
        self.speed_x = 2
        self.speed_y = 0
        self.movement_timer = 0
        self.entered = False
        
        # Attack patterns
        self.bullets = []
        self.attack_timer = 0
        self.current_phase = 1
        self.phase_transition = False
        
        # Create collision rect
        self.rect = pygame.Rect(self.x - self.width // 2, self.y - self.height // 2,
                                self.width, self.height)
        
        # Load placeholder image
        self.image = None
        self.load_assets()
        
    def set_stats(self):
        """Set boss stats based on type"""
        if self.boss_type == "mini":
            self.max_health = 300
            self.health = self.max_health
            self.score_value = 1000
            self.damage = 15
            self.max_phases = 2
        elif self.boss_type == "final":
            self.max_health = 1000
            self.health = self.max_health
            self.score_value = 5000
            self.damage = 25
            self.max_phases = 3
            self.width = 150
            self.height = 150
            
    def load_assets(self):
        """Load boss sprite"""
        import os
        boss_image_path = os.path.join("assets", "images", "basic-enemy.png")
        
        if os.path.exists(boss_image_path):
            try:
                self.image = pygame.image.load(boss_image_path).convert_alpha()
                self.image = pygame.transform.scale(self.image, (self.width, self.height))
            except:
                # Fallback to colored surface
                self.image = pygame.Surface((self.width, self.height))
                if self.boss_type == "mini":
                    self.image.fill((255, 150, 0))  # Orange
                elif self.boss_type == "final":
                    self.image.fill((200, 0, 200))  # Purple
        else:
            # Fallback to colored surface
            self.image = pygame.Surface((self.width, self.height))
            if self.boss_type == "mini":
                self.image.fill((255, 150, 0))  # Orange
            elif self.boss_type == "final":
                self.image.fill((200, 0, 200))  # Purple
            
    def update(self):
        """Update boss behavior"""
        self.movement_timer += 1
        self.attack_timer += 1
        
        # Entry movement
        if not self.entered:
            if self.y < 100:
                self.y += 2
            else:
                self.entered = True
                
        # Side-to-side movement
        if self.entered:
            self.x += self.speed_x
            if self.x <= 100 or self.x >= 700:
                self.speed_x *= -1
                
        # Update rect
        self.rect.x = self.x - self.width // 2
        self.rect.y = self.y - self.height // 2
        
        # Check for phase transitions
        health_percent = self.health / self.max_health
        if health_percent <= 0.66 and self.current_phase == 1:
            self.current_phase = 2
            self.phase_transition = True
        elif health_percent <= 0.33 and self.current_phase == 2 and self.max_phases >= 3:
            self.current_phase = 3
            self.phase_transition = True
            
        # Execute attack patterns
        self.execute_attack_pattern()
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.y > 610 or bullet.y < -10 or bullet.x < -10 or bullet.x > 810:
                self.bullets.remove(bullet)
                
    def execute_attack_pattern(self):
        """Execute attack patterns based on boss type and phase"""
        if self.boss_type == "mini":
            self.mini_boss_attacks()
        elif self.boss_type == "final":
            self.final_boss_attacks()
            
    def mini_boss_attacks(self):
        """Mini-boss attack patterns"""
        if self.current_phase == 1:
            # Phase 1: Spread shot
            if self.attack_timer % 90 == 0:
                self.spread_shot(5)
        elif self.current_phase == 2:
            # Phase 2: Faster spread + aimed shots
            if self.attack_timer % 60 == 0:
                self.spread_shot(7)
            if self.attack_timer % 45 == 0:
                self.aimed_shot()
                
    def final_boss_attacks(self):
        """Final boss attack patterns"""
        if self.current_phase == 1:
            # Phase 1: Fast bullets
            if self.attack_timer % 30 == 0:
                self.rapid_fire()
        elif self.current_phase == 2:
            # Phase 2: Circle burst
            if self.attack_timer % 120 == 0:
                self.circle_burst(16)
            if self.attack_timer % 50 == 0:
                self.aimed_shot()
        elif self.current_phase == 3:
            # Phase 3: Laser sweep + spiral
            if self.attack_timer % 90 == 0:
                self.spiral_attack()
            if self.attack_timer % 180 == 0:
                self.laser_sweep()
                
    def spread_shot(self, num_bullets):
        """Fire bullets in a spread pattern"""
        angle_step = 180 / (num_bullets - 1)
        start_angle = 90 - 90  # Start from left
        
        for i in range(num_bullets):
            angle = math.radians(start_angle + (i * angle_step))
            speed = 5
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            
            bullet = BossBullet(self.x, self.y + self.height // 2, speed_x, speed_y)
            self.bullets.append(bullet)
            
    def circle_burst(self, num_bullets):
        """Fire bullets in a complete circle"""
        angle_step = 360 / num_bullets
        
        for i in range(num_bullets):
            angle = math.radians(i * angle_step)
            speed = 4
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            
            bullet = BossBullet(self.x, self.y, speed_x, speed_y)
            self.bullets.append(bullet)
            
    def aimed_shot(self):
        """Fire a bullet aimed at player position (placeholder)"""
        # For now, just shoot straight down
        # TODO: Add player targeting when integrated
        bullet = BossBullet(self.x, self.y + self.height // 2, 0, 6)
        self.bullets.append(bullet)
        
    def rapid_fire(self):
        """Fire multiple bullets quickly"""
        for i in range(3):
            offset_x = (i - 1) * 20
            bullet = BossBullet(self.x + offset_x, self.y + self.height // 2, 0, 8)
            self.bullets.append(bullet)
            
    def spiral_attack(self):
        """Create a spiral pattern of bullets"""
        num_arms = 4
        for arm in range(num_arms):
            angle = math.radians((self.attack_timer * 3 + arm * 90) % 360)
            speed = 4
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            
            bullet = BossBullet(self.x, self.y, speed_x, speed_y, "spiral")
            self.bullets.append(bullet)
            
    def laser_sweep(self):
        """Create a sweeping laser effect"""
        # Create multiple bullets in a line that sweeps across
        for i in range(5):
            angle = math.radians(70 + (self.movement_timer % 40))
            speed = 6
            speed_x = math.cos(angle) * speed
            speed_y = math.sin(angle) * speed
            
            bullet = BossBullet(self.x, self.y, speed_x, speed_y)
            self.bullets.append(bullet)
            
    def take_damage(self, damage):
        """Take damage from player weapons"""
        self.health -= damage
        self.health = max(0, self.health)
        
        if self.phase_transition:
            self.phase_transition = False
            
    def draw(self, screen):
        """Draw the boss and its bullets"""
        # Draw boss
        screen.blit(self.image, (self.rect.x, self.rect.y))
        
        # Draw health bar
        bar_width = self.width
        bar_height = 10
        bar_x = self.rect.x
        bar_y = self.rect.y - 20
        
        # Background
        pygame.draw.rect(screen, (100, 100, 100), (bar_x, bar_y, bar_width, bar_height))
        # Current health
        current_width = int((self.health / self.max_health) * bar_width)
        
        # Color changes based on health
        if self.health / self.max_health > 0.5:
            health_color = (0, 255, 0)
        elif self.health / self.max_health > 0.25:
            health_color = (255, 255, 0)
        else:
            health_color = (255, 0, 0)
            
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, current_width, bar_height))
        # Border
        pygame.draw.rect(screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Phase indicator
        font = pygame.font.Font(None, 24)
        phase_text = font.render(f"Phase {self.current_phase}/{self.max_phases}", True, (255, 255, 255))
        screen.blit(phase_text, (bar_x, bar_y - 25))
        
        # Draw bullets
        for bullet in self.bullets:
            bullet.draw(screen)
