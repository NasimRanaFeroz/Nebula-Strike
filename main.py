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
            'game_bg': 'Starscape.png',
            'logo': 'logo.png',
            'player': 'main-spacecraft.png',
            'shield': 'shield.png',
            'enemy_basic': 'basic-enemy.png',
            'enemy_2': 'enemy-2.png',
            'bullet': 'bullet1.png',
            'destruction': 'destruction.png',
            'bg': 'bg.png',
            'enemy_ship': 'enemyShip.png',
            'enemy_ufo': 'enemyUFO.png',
            'starscape': 'Starscape.png'
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
        
        # Initialize sound mixer
        try:
            pygame.mixer.init()
            self.sound_enabled = True
        except:
            self.sound_enabled = False
        
        # Load sound effects
        self.sounds = {}
        sound_path = "assets/sounds"
        sound_files = {
            'shoot': 'shoot.wav',
            'shoot_laser': 'shootLaser.wav',
            'enemy_kill': 'enemyKill.wav',
            'fighter_kill': 'fighterKill.wav',
            'hit': 'hit.wav'
        }
        
        for key, filename in sound_files.items():
            filepath = os.path.join(sound_path, filename)
            if os.path.exists(filepath) and self.sound_enabled:
                try:
                    self.sounds[key] = pygame.mixer.Sound(filepath)
                    self.sounds[key].set_volume(0.3)
                except:
                    self.sounds[key] = None
            else:
                self.sounds[key] = None
        
        # Load background music
        bg_music_path = os.path.join(sound_path, 'background.mp3')
        if os.path.exists(bg_music_path) and self.sound_enabled:
            try:
                pygame.mixer.music.load(bg_music_path)
                pygame.mixer.music.set_volume(0.2)
            except:
                pass
        
    def new_game(self):
        """Start a new game"""
        self.player = Player(SCREEN_WIDTH // 2, SCREEN_HEIGHT - 100)
        self.enemy_manager = EnemyManager()
        self.level_manager = LevelManager(self.selected_level)
        self.powerup_manager = PowerUpManager()
        self.level = self.selected_level
        self.score = 0
        self.game_state = "playing"
        
        # Start background music
        if self.sound_enabled:
            try:
                pygame.mixer.music.play(-1)  # Loop indefinitely
            except:
                pass
        
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
                elif event.key == pygame.K_m:
                    if self.game_state == "paused":
                        pygame.mixer.music.stop()
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
                if self.sound_enabled and self.sounds.get('fighter_kill'):
                    self.sounds['fighter_kill'].play()
                    
        # Update level manager
        if self.level_manager:
            enemies_spawned = self.level_manager.update(self.enemy_manager)
            for enemy_data in enemies_spawned:
                self.enemy_manager.spawn_enemy(enemy_data)
            
            # Check for boss
            boss = self.level_manager.get_current_level().get_boss()
            if boss:
                boss.update()
                # Check if boss is defeated
                if boss.health <= 0 and not self.level_manager.get_current_level().completed:
                    self.level_manager.get_current_level().completed = True
                    self.score += boss.score_value
                    if self.sound_enabled and self.sounds.get('enemy_kill'):
                        self.sounds['enemy_kill'].play()
            
            # Check if level/game is complete
            if self.level_manager.is_game_complete():
                self.game_state = "victory"
            elif self.level_manager.get_current_level().is_completed():
                # Level complete, advance
                if self.level < 3:
                    self.level += 1
                    self.level_manager.advance_level()
                
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
            
        # Check boss collisions
        boss = None
        if self.level_manager:
            boss = self.level_manager.get_current_level().get_boss()
            if boss and boss.health > 0:
                # Player bullets hit boss
                for bullet in self.player.bullets[:]:
                    if self.check_collision(bullet, boss):
                        boss.take_damage(bullet.damage)
                        if bullet in self.player.bullets:
                            self.player.bullets.remove(bullet)
                        if self.sound_enabled and self.sounds.get('hit'):
                            self.sounds['hit'].play()
                
                # Boss bullets hit player
                for bullet in boss.bullets[:]:
                    if self.check_collision(bullet, self.player):
                        if not self.player.is_shielded():
                            self.player.take_damage(bullet.damage)
                            if self.sound_enabled and self.sounds.get('hit'):
                                self.sounds['hit'].play()
                        boss.bullets.remove(bullet)
            
        # Player bullets hit enemies
        for bullet in self.player.bullets[:]:
            for enemy in self.enemy_manager.enemies[:]:
                if self.check_collision(bullet, enemy):
                    enemy.take_damage(bullet.damage)
                    if bullet in self.player.bullets:
                        self.player.bullets.remove(bullet)
                    if self.sound_enabled and self.sounds.get('hit'):
                        self.sounds['hit'].play()
                    if enemy.health <= 0:
                        self.score += enemy.score_value
                        self.enemy_manager.enemies.remove(enemy)
                        if self.sound_enabled and self.sounds.get('enemy_kill'):
                            self.sounds['enemy_kill'].play()
                        # Chance to drop power-up
                        if self.powerup_manager:
                            self.powerup_manager.try_spawn(enemy.x, enemy.y)
                            
        # Enemy bullets hit player
        for enemy in self.enemy_manager.enemies:
            for bullet in enemy.bullets[:]:
                if self.check_collision(bullet, self.player):
                    if not self.player.is_shielded():
                        self.player.take_damage(bullet.damage)
                        if self.sound_enabled and self.sounds.get('hit'):
                            self.sounds['hit'].play()
                    enemy.bullets.remove(bullet)
                    
        # Enemies collide with player
        for enemy in self.enemy_manager.enemies:
            if self.check_collision(enemy, self.player):
                if not self.player.is_shielded():
                    self.player.take_damage(20)
                    if self.sound_enabled and self.sounds.get('hit'):
                        self.sounds['hit'].play()
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
        elif bg_type == "game" and self.assets.get('starscape'):
            bg = pygame.transform.scale(self.assets['starscape'], (SCREEN_WIDTH, SCREEN_HEIGHT))
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
            self.screen.fill(BLACK)
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
        elif self.game_state == "victory":
            self.draw_background("game")
            self.draw_victory()
            
        pygame.display.flip()
        
    def draw_menu(self):
        """Draw main menu"""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        font_small = pygame.font.Font(None, 36)
        font_author = pygame.font.Font(None, 36)
        
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
        
        # Author name
        author_text = "By Nasim Rana Feroz"
        # Draw black stroke
        author_stroke = font_author.render(author_text, True, BLACK)
        for offset_x in [-2, 0, 2]:
            for offset_y in [-2, 0, 2]:
                if offset_x != 0 or offset_y != 0:
                    self.screen.blit(author_stroke, (SCREEN_WIDTH // 2 - author_stroke.get_width() // 2 + offset_x, 320 + offset_y))
        # Draw white text on top
        author = font_author.render(author_text, True, WHITE)
        self.screen.blit(author, (SCREEN_WIDTH // 2 - author.get_width() // 2, 320))
        
        subtitle = font_medium.render("Press SPACE to Start", True, WHITE)
        self.screen.blit(subtitle, (SCREEN_WIDTH // 2 - subtitle.get_width() // 2, 420))
        
        # Instructions
        instructions = font_small.render("ESC to Quit", True, WHITE)
        self.screen.blit(instructions, (SCREEN_WIDTH // 2 - instructions.get_width() // 2, 540))
        
    def draw_level_select(self):
        """Draw level selection screen"""
        font_title = pygame.font.Font(None, 56)
        font_level = pygame.font.Font(None, 42)
        font_desc = pygame.font.Font(None, 26)
        font_small = pygame.font.Font(None, 22)
        
        # Animated stars in background
        for i in range(100):
            x = (i * 47 + self.bg_scroll // 2) % SCREEN_WIDTH
            y = (i * 73 + self.bg_scroll) % SCREEN_HEIGHT
            size = 1 + (i % 3)
            brightness = 100 + (i % 156)
            pygame.draw.circle(self.screen, (brightness, brightness, brightness), (x, y), size)
        
        # Title with glow effect
        title_padding_top = 40
        title_text = "SELECT MISSION"
        
        # Create glowing title effect
        for glow_size in range(5, 0, -1):
            glow_alpha = 30
            title_glow = font_title.render(title_text, True, (0, 150, 255))
            title_glow.set_alpha(glow_alpha)
            self.screen.blit(title_glow, (SCREEN_WIDTH // 2 - title_glow.get_width() // 2 - glow_size, 
                                          title_padding_top - glow_size))
        
        title = font_title.render(title_text, True, (100, 220, 255))
        self.screen.blit(title, (SCREEN_WIDTH // 2 - title.get_width() // 2, title_padding_top))
        
        # Decorative lines under title
        line_y = title_padding_top + 60
        pygame.draw.line(self.screen, (100, 220, 255), 
                        (SCREEN_WIDTH // 2 - 140, line_y), 
                        (SCREEN_WIDTH // 2 + 140, line_y), 3)
        pygame.draw.line(self.screen, (50, 110, 180), 
                        (SCREEN_WIDTH // 2 - 140, line_y + 2), 
                        (SCREEN_WIDTH // 2 + 140, line_y + 2), 1)
        
        # Level cards with enhanced design
        y_start = 150
        y_spacing = 140
        card_width = 480
        card_height = 100
        
        level_data = [
            {"name": "LEVEL 1", "subtitle": "Initial Contact", 
             "difficulty": "★ EASY", "color": (0, 255, 150), "accent": (0, 180, 100)},
            {"name": "LEVEL 2", "subtitle": "Advanced Threats", 
             "difficulty": "★★ MEDIUM", "color": (255, 220, 0), "accent": (200, 150, 0)},
            {"name": "LEVEL 3", "subtitle": "Final Showdown", 
             "difficulty": "★★★ HARD", "color": (255, 80, 80), "accent": (200, 30, 30)}
        ]
        
        for i, data in enumerate(level_data):
            card_x = (SCREEN_WIDTH - card_width) // 2
            card_y = y_start + i * y_spacing
            
            # Create card surface with transparency
            card_surface = pygame.Surface((card_width, card_height), pygame.SRCALPHA)
            
            # Draw card background with dark gradient
            for j in range(card_height):
                alpha = int(120 + (j / card_height) * 60)
                dark_val = int(20 + (j / card_height) * 20)
                color = (dark_val, dark_val, dark_val, alpha)
                pygame.draw.rect(card_surface, color, (0, j, card_width, 1))
            
            # Draw accent line on left
            for y_offset in range(card_height):
                alpha = int(180 + (y_offset / card_height) * 75)
                accent_color = (*data["accent"], alpha)
                pygame.draw.rect(card_surface, accent_color, (0, y_offset, 6, 1))
            
            # Draw glowing border
            pygame.draw.rect(card_surface, data["color"], (0, 0, card_width, card_height), 2)
            
            # Inner glow
            inner_glow = pygame.Surface((card_width - 4, card_height - 4), pygame.SRCALPHA)
            pygame.draw.rect(inner_glow, (*data["accent"], 40), (0, 0, card_width - 4, card_height - 4), 1)
            card_surface.blit(inner_glow, (2, 2))
            
            # Blit card to screen
            self.screen.blit(card_surface, (card_x, card_y))
            
            # Level number badge
            badge_size = 55
            badge_x = card_x + 20
            badge_y = card_y + (card_height - badge_size) // 2
            
            # Badge background circle
            pygame.draw.circle(self.screen, data["accent"], (badge_x + badge_size // 2, badge_y + badge_size // 2), badge_size // 2)
            pygame.draw.circle(self.screen, data["color"], (badge_x + badge_size // 2, badge_y + badge_size // 2), badge_size // 2, 2)
            
            # Number in badge
            level_num = font_level.render(f"{i + 1}", True, WHITE)
            num_x = badge_x + (badge_size - level_num.get_width()) // 2
            num_y = badge_y + (badge_size - level_num.get_height()) // 2
            self.screen.blit(level_num, (num_x, num_y))
            
            # Level name and subtitle
            name_text = font_level.render(data["name"], True, data["color"])
            subtitle_text = font_desc.render(data["subtitle"], True, (180, 180, 180))
            difficulty_text = font_small.render(data["difficulty"], True, data["color"])
            
            self.screen.blit(name_text, (card_x + 95, card_y + 18))
            self.screen.blit(subtitle_text, (card_x + 95, card_y + 55))
            self.screen.blit(difficulty_text, (card_x + card_width - 110, card_y + 40))
        
        # Instructions at bottom with styled background
        instruction_y = SCREEN_HEIGHT - 50
        instruction = font_small.render("Press 1, 2, or 3 to select | ESC to go back", True, (180, 180, 180))
        
        # Instruction background
        instruction_bg = pygame.Surface((instruction.get_width() + 30, 35), pygame.SRCALPHA)
        instruction_bg.fill((30, 30, 30, 200))
        pygame.draw.rect(instruction_bg, (100, 220, 255), (0, 0, instruction.get_width() + 30, 35), 2)
        
        self.screen.blit(instruction_bg, 
                        (SCREEN_WIDTH // 2 - instruction.get_width() // 2 - 15, instruction_y - 10))
        self.screen.blit(instruction, (SCREEN_WIDTH // 2 - instruction.get_width() // 2, instruction_y))
        
    def draw_game(self):
        """Draw game elements"""
        # Draw all game objects
        if self.player:
            self.player.draw(self.screen)
        if self.enemy_manager:
            self.enemy_manager.draw(self.screen)
        if self.powerup_manager:
            self.powerup_manager.draw(self.screen)
        
        # Draw boss if active
        if self.level_manager:
            boss = self.level_manager.get_current_level().get_boss()
            if boss and boss.health > 0:
                boss.draw(self.screen)
            
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
        # Semi-transparent overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 180))
        self.screen.blit(overlay, (0, 0))
        
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 42)
        font_small = pygame.font.Font(None, 32)
        
        # Title
        pause_text = font_large.render("PAUSED", True, (100, 200, 255))
        self.screen.blit(pause_text, (SCREEN_WIDTH // 2 - pause_text.get_width() // 2, 200))
        
        # Resume button
        resume_text = font_medium.render("Press ESC to Resume", True, WHITE)
        resume_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 350, 400, 60)
        pygame.draw.rect(self.screen, (0, 100, 200), resume_rect, 3)
        self.screen.blit(resume_text, (SCREEN_WIDTH // 2 - resume_text.get_width() // 2, 365))
        
        # Main menu button
        menu_text = font_medium.render("Press M for Main Menu", True, WHITE)
        menu_rect = pygame.Rect(SCREEN_WIDTH // 2 - 200, 450, 400, 60)
        pygame.draw.rect(self.screen, (200, 100, 0), menu_rect, 3)
        self.screen.blit(menu_text, (SCREEN_WIDTH // 2 - menu_text.get_width() // 2, 465))
        
        # Score display
        score_text = font_small.render(f"Current Score: {self.score}", True, (200, 200, 200))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 580))
        
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
    
    def draw_victory(self):
        """Draw victory screen"""
        font_large = pygame.font.Font(None, 64)
        font_small = pygame.font.Font(None, 36)
        
        victory = font_large.render("VICTORY!", True, GREEN)
        score_text = font_small.render(f"Final Score: {self.score}", True, WHITE)
        high_score_text = font_small.render(f"High Score: {self.high_score}", True, WHITE)
        congrats = font_small.render("All Levels Complete!", True, WHITE)
        restart = font_small.render("Press SPACE to Play Again", True, WHITE)
        
        self.screen.blit(victory, (SCREEN_WIDTH // 2 - victory.get_width() // 2, 150))
        self.screen.blit(congrats, (SCREEN_WIDTH // 2 - congrats.get_width() // 2, 230))
        self.screen.blit(score_text, (SCREEN_WIDTH // 2 - score_text.get_width() // 2, 300))
        self.screen.blit(high_score_text, (SCREEN_WIDTH // 2 - high_score_text.get_width() // 2, 340))
        self.screen.blit(restart, (SCREEN_WIDTH // 2 - restart.get_width() // 2, 450))
        
        if pygame.key.get_pressed()[pygame.K_SPACE]:
            self.game_state = "menu"
        
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
