"""
Nebula Strike - A Vertical Scrolling Space Shooter
Main game entry point and game loop
"""

try:
    import pygame
except ImportError:
    import pygame_ce as pygame
import sys
import os
from src.player import Player
from src.enemy import EnemyManager
from src.level import LevelManager
from src.powerup import PowerUpManager

# Game Constants
SCREEN_WIDTH = 600
SCREEN_HEIGHT = 800
FPS = 60
TITLE = "Nebula Strike"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 100, 255)


class Game:
    """Main game class managing all game states and components"""
    
    def __init__(self):
        """Initialize the game"""
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.running = True
        self.game_state = "menu"  # menu, level_select, playing, paused, game_over, victory
        
        # Game objects
        self.player = None
        self.enemy_manager = None
        self.level_manager = None
        self.powerup_manager = None
        
        # Score and stats
        self.score = 0
        self.high_score = 0
        self.level = 1
        self.selected_level = 1
        
        # Background scrolling
        self.bg_scroll = 0
        self.bg_speed = 2
        
        # Load assets
        self.load_assets()
        
    def load_assets(self):
        """Load game assets"""
        self.assets = {}
        asset_path = "assets/images"
        
        # Try to load images if they exist
        asset_files = {
            'menu_bg': 'menu-bg.png',
            'game_bg': 'game-bg.png',
            'logo': 'logo.png',
            'player': 'main-spacecraft.png',
            'shield': 'shield.png',
            'enemy_basic': 'basic-enemy.png',
            'enemy_2': 'enemy-2.png',
            'bullet': 'bullet1.png',
            'destruction': 'destruction.png',
            'bg': 'bg.png'
        }
        
        for key, filename in asset_files.items():
            filepath = os.path.join(asset_path, filename)
            if os.path.exists(filepath):
                try:
                    self.assets[key] = pygame.image.load(filepath).convert_alpha()
                except:
                    self.assets[key] = None
            else:
                self.assets[key] = None
        
    def new_game(self):
        """Start a new game"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemy_manager = EnemyManager()
        self.level_manager = LevelManager(self.selected_level)
        self.powerup_manager = PowerUpManager()
        self.level = self.selected_level
        self.score = 0
        self.game_state = "playing"
        
    def handle_events(self):
        """Handle all game events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.game_state == "playing":
                        self.game_state = "paused"
                    elif self.game_state == "paused":
                        self.game_state = "playing"
                    elif self.game_state == "level_select":
                        self.game_state = "menu"
                elif event.key == pygame.K_SPACE:
                    if self.game_state == "menu":
                        self.game_state = "level_select"
                    elif self.game_state == "playing" and self.player:
                        self.player.shoot()
                elif event.key == pygame.K_LSHIFT:
                    if self.game_state == "playing" and self.player:
                        self.player.use_special_weapon()
                elif event.key == pygame.K_1:
                    if self.game_state == "level_select":
                        self.selected_level = 1
                        self.new_game()
                elif event.key == pygame.K_2:
                    if self.game_state == "level_select":
                        self.selected_level = 2
                        self.new_game()
                elif event.key == pygame.K_3:
                    if self.game_state == "level_select":
                        self.selected_level = 3
                        self.new_game()
                        
    def update(self):
        """Update all game objects"""
        if self.game_state != "playing":
            return
            
        # Update background scroll
        self.bg_scroll += self.bg_speed
        if self.bg_scroll >= SCREEN_HEIGHT:
            self.bg_scroll = 0
            
        # Update player
        if self.player:
            self.player.update()
            if self.player.health <= 0:
                self.game_state = "game_over"
                if self.score > self.high_score:
                    self.high_score = self.score
                    
        # Update level manager
        if self.level_manager:
            enemies_spawned = self.level_manager.update()
            for enemy_data in enemies_spawned:
                self.enemy_manager.spawn_enemy(enemy_data)
                
        # Update enemies
        if self.enemy_manager:
            self.enemy_manager.update()
            
        # Update power-ups
        if self.powerup_manager:
            self.powerup_manager.update()
            
        # Check collisions
        self.check_collisions()
        
    def check_collisions(self):
        """Check for collisions between game objects"""
        if not self.player or not self.enemy_manager:
            return
            
        # Player bullets hit enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemy_manager.enemies[:]:
                if self.check_collision(bullet, enemy):
                    enemy.take_damage(bullet.damage)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if enemy.health <= 0:
                        self.score += enemy.score_value
                        self.enemy_manager.enemies.remove(enemy)
                        # Chance to drop power-up
                        if self.powerup_manager:
                            self.powerup_manager.try_spawn(enemy.x, enemy.y)
                            
        # Enemy bullets hit player
        for enemy in self.enemy_manager.enemies:
            for bullet in enemy.bullets[:]:
                if self.check_collision(bullet, self.player):
                    if not self.player.is_shielded():
                        self.player.take_damage(bullet.damage)
                    enemy.bullets.remove(bullet)
                    
        # Enemies collide with player
        for enemy in self.enemy_manager.enemies:
            if self.check_collision(enemy, self.player):
                if not self.player.is_shielded():
                    self.player.take_damage(20)
                enemy.take_damage(enemy.health)
                
        # Player collects power-ups
        if self.powerup_manager:
            for powerup in self.powerup_manager.powerups[:]:
                if self.check_collision(powerup, self.player):
                    self.player.apply_powerup(powerup)
                    self.powerup_manager.powerups.remove(powerup)
                    
    def check_collision(self, obj1, obj2):
        """Check collision between two objects with rect attributes"""
        if hasattr(obj1, 'rect') and hasattr(obj2, 'rect'):
            return obj1.rect.colliderect(obj2.rect)
        return False
        
    def draw_background(self, bg_type="game"):
        """Draw scrolling background"""
        # Try to use loaded background images
        if bg_type == "menu" and self.assets.get('menu_bg'):
            bg = pygame.transform.scale(self.assets['menu_bg'], (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(bg, (0, 0))
        elif bg_type == "game" and self.assets.get('game_bg'):
            bg = pygame.transform.scale(self.assets['game_bg'], (SCREEN_WIDTH, SCREEN_HEIGHT))
            self.screen.blit(bg, (0, self.bg_scroll - SCREEN_HEIGHT))
            self.screen.blit(bg, (0, self.bg_scroll))
        else:
            # Fallback: Draw starfield background
            self.screen.fill(BLACK)
            for i in range(50):
                x = (i * 37) % SCREEN_WIDTH
                y = (i * 59 + self.bg_scroll) % SCREEN_HEIGHT
                pygame.draw.circle(self.screen, WHITE, (x, y), 1)
            
    def draw(self):
        """Draw all game objects"""
        if self.game_state == "menu":
            self.draw_background("menu")
            self.draw_menu()
        elif self.game_state == "level_select":
            self.draw_background("menu")
            self.draw_level_select()
        elif self.game_state == "playing":
            self.draw_background("game")
            self.draw_game()
        elif self.game_state == "paused":
            self.draw_background("game")
            self.draw_game()
            self.draw_pause()
        elif self.game_state == "game_over":
            self.draw_background("game")
            self.draw_game_over()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Draw main menu"""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        
        # Draw logo if available
        logo_top_padding = 60
        logo_height = 240
        
        if self.assets.get('logo'):
            logo = self.assets['logo']
            # Scale logo to fixed height while maintaining aspect ratio
            aspect_ratio = logo.get_width() / logo.get_height()
            logo_width = int(logo_height * aspect_ratio)
            logo = pygame.transform.scale(logo, (logo_width, logo_height))
            logo_x = (SCREEN_WIDTH - logo_width) // 2
            self.screen.blit(logo, (logo_x, logo_top_padding))
        else:
            title = font_large.render("NEBULA STRIKE", True, BLUE)
            self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, logo_top_padding))
        
        subtitle = font_medium.render("Press SPACE to Start", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 420))
        
        # Instructions
        instructions = font_small.render("ESC to Quit", True, WHITE)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 540))
        
    def draw_level_select(self):
        """Draw level selection screen"""
        font_large = pygame.font.Font(None, 64)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 28)
        
        # Title with top padding - centered vertically
        title_padding_top = 120
        title = font_large.render("SELECT LEVEL", True, BLUE)
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_padding_top))
        
        # Level buttons with better spacing
        y_start = 240
        y_spacing = 130
        button_padding = 25
        
        for i in range(1, 4):
            level_text = font_medium.render(f"Level {i}", True, WHITE)
            level_x = SCREEN_WIDTH // 2 - level_text.get_width() // 2
            level_y = y_start + (i - 1) * y_spacing
            
            # Draw button background with padding
            button_rect = pygame.Rect(level_x - button_padding, level_y - 15, 
                                     level_text.get_width() + button_padding * 2, 
                                     level_text.get_height() + 30)
            pygame.draw.rect(self.screen, BLUE, button_rect, 3)
            
            # Draw text
            self.screen.blit(level_text, (level_x, level_y))
            
            # Draw level description with margin
            descriptions = [
                "Initial Contact",
                "Advanced Threats",
                "Final Showdown"
            ]
            desc_text = font_small.render(descriptions[i-1], True, WHITE)
            self.screen.blit(desc_text, (SCREEN_WIDTH // 2 - desc_text.get_width() // 2, level_y + 50))
        
        # Instructions at bottom with padding
        instruction = font_small.render("Press 1, 2, or 3 | ESC to go back", True, WHITE)
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, SCREEN_HEIGHT - 80))
        
    def draw_game(self):
        """Draw game elements"""
        # Draw all game objects
        if self.player:
            self.player.draw(self.screen)
        if self.enemy_manager:
            self.enemy_manager.draw(self.screen)
        if self.powerup_manager:
            self.powerup_manager.draw(self.screen)
            
        # Draw HUD
        self.draw_hud()
        
    def draw_hud(self):
        """Draw heads-up display"""
        font = pygame.font.Font(None, 32)
        
        # Score
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        
        # Level
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        self.screen.blit(level_text, (10, 40))
        
        # Health bar
        if self.player:
            health_width = 200
            health_height = 20
            health_x = SCREEN_WIDTH - health_width - 10
            health_y = 10
            
            # Background
            pygame.draw.rect(self.screen, RED, (health_x, health_y, health_width, health_height))
            # Current health
            current_width = int((self.player.health / self.player.max_health) * health_width)
            pygame.draw.rect(self.screen, GREEN, (health_x, health_y, current_width, health_height))
            # Border
            pygame.draw.rect(self.screen, WHITE, (health_x, health_y, health_width, health_height), 2)
            
    def draw_pause(self):
        """Draw pause overlay"""
        font = pygame.font.Font(None, 64)
        pause_text = font.render("PAUSED", True, WHITE)
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, SCREEN_HEIGHT // 2))
        
    def draw_game_over(self):
        """Draw game over screen"""
        font_large = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 36)
        
        game_over = font_large.render("GAME OVER", True, RED)
        score_text = font_small.render(f"Final Score: {self.score}", True, WHITE)
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, WHITE)
        restart = font_small.render("Press SPACE to Restart", True, WHITE)
        
        self.screen.blit(game_over, (SCREEN_WIDTH // 2 - game_over.get_width() // 2, 150))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 280))
        self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 320))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 400))
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.new_game()
        
    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
            
        pygame.quit()
        sys.exit()


if __name__ == "__main__":
    game = Game()
    game.run()
