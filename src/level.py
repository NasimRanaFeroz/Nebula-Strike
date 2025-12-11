try:
    import pygame
except ImportError:
    import pygame_ce as pygame
from src.boss import Boss


class Wave:
    """Represents a wave of enemies"""
    
    def __init__(self, wave_data):
        """Initialize wave with enemy spawn data"""
        self.enemies = wave_data.get("enemies", [])
        self.spawn_delay = wave_data.get("spawn_delay", 60)  # Frames between spawns
        self.spawn_timer = 0
        self.current_spawn_index = 0
        self.completed = False
        
    def update(self):
        """Update wave and return enemies to spawn"""
        if self.completed:
            return []
            
        self.spawn_timer += 1
        enemies_to_spawn = []
        
        if self.spawn_timer >= self.spawn_delay and self.current_spawn_index < len(self.enemies):
            enemies_to_spawn.append(self.enemies[self.current_spawn_index])
            self.current_spawn_index += 1
            self.spawn_timer = 0
            
            if self.current_spawn_index >= len(self.enemies):
                self.completed = True
                
        return enemies_to_spawn
        
    def is_completed(self):
        """Check if wave is complete"""
        return self.completed


class Level:
    """Represents a game level with multiple waves"""
    
    def __init__(self, level_num):
        """Initialize level"""
        self.level_num = level_num
        self.waves = []
        self.current_wave_index = 0
        self.wave_delay_timer = 0
        self.wave_delay = 180  # Frames between waves
        self.boss_spawned = False
        self.boss = None
        self.completed = False
        
        # Build level waves
        self.build_level()
        
    def build_level(self):
        """Build waves for this level"""
        if self.level_num == 1:
            self.build_level_1()
        elif self.level_num == 2:
            self.build_level_2()
        elif self.level_num == 3:
            self.build_level_3()
            
    def build_level_1(self):
        """Level 1: Initial Contact - 3 waves + mini-boss"""
        # Wave 1: Basic enemies
        wave1_data = {
            "enemies": [
                {"x": 200, "y": -50, "type": "basic"},
                {"x": 400, "y": -50, "type": "basic"},
                {"x": 600, "y": -50, "type": "basic"},
                {"x": 300, "y": -100, "type": "basic"},
                {"x": 500, "y": -100, "type": "basic"},
            ],
            "spawn_delay": 40
        }
        self.waves.append(Wave(wave1_data))
        
        # Wave 2: More basic enemies in formation
        wave2_data = {
            "enemies": [
                {"x": 150, "y": -50, "type": "basic"},
                {"x": 250, "y": -50, "type": "basic"},
                {"x": 350, "y": -50, "type": "basic"},
                {"x": 450, "y": -50, "type": "basic"},
                {"x": 550, "y": -50, "type": "basic"},
                {"x": 650, "y": -50, "type": "basic"},
            ],
            "spawn_delay": 35
        }
        self.waves.append(Wave(wave2_data))
        
        # Wave 3: Mixed enemies
        wave3_data = {
            "enemies": [
                {"x": 200, "y": -50, "type": "basic"},
                {"x": 400, "y": -50, "type": "zigzag"},
                {"x": 600, "y": -50, "type": "basic"},
                {"x": 300, "y": -100, "type": "zigzag"},
                {"x": 500, "y": -100, "type": "basic"},
                {"x": 400, "y": -150, "type": "elite"},
            ],
            "spawn_delay": 45
        }
        self.waves.append(Wave(wave3_data))
        
    def build_level_2(self):
        """Level 2: Advanced Threats - Zig-zag enemies and elite shooters"""
        # Wave 1: Zig-zag formation
        wave1_data = {
            "enemies": [
                {"x": 100, "y": -50, "type": "zigzag"},
                {"x": 300, "y": -50, "type": "zigzag"},
                {"x": 500, "y": -50, "type": "zigzag"},
                {"x": 700, "y": -50, "type": "zigzag"},
                {"x": 200, "y": -100, "type": "basic"},
                {"x": 400, "y": -100, "type": "basic"},
                {"x": 600, "y": -100, "type": "basic"},
            ],
            "spawn_delay": 40
        }
        self.waves.append(Wave(wave1_data))
        
        # Wave 2: Elite shooters
        wave2_data = {
            "enemies": [
                {"x": 200, "y": -50, "type": "elite"},
                {"x": 400, "y": -50, "type": "elite"},
                {"x": 600, "y": -50, "type": "elite"},
                {"x": 300, "y": -100, "type": "zigzag"},
                {"x": 500, "y": -100, "type": "zigzag"},
            ],
            "spawn_delay": 50
        }
        self.waves.append(Wave(wave2_data))
        
        # Wave 3: Mixed advanced
        wave3_data = {
            "enemies": [
                {"x": 150, "y": -50, "type": "elite"},
                {"x": 350, "y": -50, "type": "zigzag"},
                {"x": 550, "y": -50, "type": "elite"},
                {"x": 250, "y": -100, "type": "kamikaze"},
                {"x": 450, "y": -100, "type": "kamikaze"},
                {"x": 650, "y": -100, "type": "zigzag"},
                {"x": 400, "y": -150, "type": "elite"},
            ],
            "spawn_delay": 45
        }
        self.waves.append(Wave(wave3_data))
        
    def build_level_3(self):
        """Level 3: The Final Showdown - Mixed waves leading to final boss"""
        # Wave 1: Heavy assault
        wave1_data = {
            "enemies": [
                {"x": 100, "y": -50, "type": "elite"},
                {"x": 250, "y": -50, "type": "zigzag"},
                {"x": 400, "y": -50, "type": "elite"},
                {"x": 550, "y": -50, "type": "zigzag"},
                {"x": 700, "y": -50, "type": "elite"},
                {"x": 175, "y": -100, "type": "kamikaze"},
                {"x": 325, "y": -100, "type": "kamikaze"},
                {"x": 475, "y": -100, "type": "kamikaze"},
                {"x": 625, "y": -100, "type": "kamikaze"},
            ],
            "spawn_delay": 35
        }
        self.waves.append(Wave(wave1_data))
        
        # Wave 2: Elite squadron
        wave2_data = {
            "enemies": [
                {"x": 200, "y": -50, "type": "elite"},
                {"x": 400, "y": -50, "type": "elite"},
                {"x": 600, "y": -50, "type": "elite"},
                {"x": 300, "y": -100, "type": "elite"},
                {"x": 500, "y": -100, "type": "elite"},
                {"x": 400, "y": -150, "type": "elite"},
            ],
            "spawn_delay": 60
        }
        self.waves.append(Wave(wave2_data))
        
        # Wave 3: Final wave before boss
        wave3_data = {
            "enemies": [
                {"x": 150, "y": -50, "type": "zigzag"},
                {"x": 300, "y": -50, "type": "elite"},
                {"x": 450, "y": -50, "type": "zigzag"},
                {"x": 600, "y": -50, "type": "elite"},
                {"x": 200, "y": -100, "type": "kamikaze"},
                {"x": 400, "y": -100, "type": "kamikaze"},
                {"x": 600, "y": -100, "type": "kamikaze"},
            ],
            "spawn_delay": 40
        }
        self.waves.append(Wave(wave3_data))
        
    def update(self, enemy_manager):
        """Update level progression and return enemies to spawn"""
        if self.completed:
            return []
            
        enemies_to_spawn = []
        
        # Handle boss
        if self.boss_spawned:
            if self.boss and self.boss.health <= 0:
                self.completed = True
            return []
            
        # Handle waves
        if self.current_wave_index < len(self.waves):
            current_wave = self.waves[self.current_wave_index]
            enemies_to_spawn = current_wave.update()
            
            if current_wave.is_completed():
                # Wait before next wave
                self.wave_delay_timer += 1
                if self.wave_delay_timer >= self.wave_delay:
                    self.current_wave_index += 1
                    self.wave_delay_timer = 0
        else:
            # All waves complete, spawn boss
            if not self.boss_spawned:
                self.spawn_boss()
                
        return enemies_to_spawn
        
    def spawn_boss(self):
        """Spawn the level boss"""
        self.boss_spawned = True
        if self.level_num == 1:
            self.boss = Boss(400, -100, "mini")
        elif self.level_num >= 2:
            self.boss = Boss(400, -100, "final")
            
    def is_completed(self):
        """Check if level is complete"""
        return self.completed
        
    def get_boss(self):
        """Get the current boss if active"""
        return self.boss if self.boss_spawned else None


class LevelManager:
    """Manages level progression and transitions"""
    
    def __init__(self, starting_level=1):
        """Initialize level manager"""
        self.current_level_num = starting_level
        self.current_level = Level(self.current_level_num)
        self.max_levels = 3
        self.all_levels_complete = False
        
    def update(self):
        """Update current level and return enemies to spawn"""
        if self.all_levels_complete:
            return []
            
        enemies_to_spawn = []
        
        # Update current level (enemy_manager passed in main game loop)
        # For now, return empty list - will be integrated with main game
        
        # Check for level completion
        if self.current_level.is_completed():
            if self.current_level_num >= self.max_levels:
                self.all_levels_complete = True
            else:
                # Advance to next level
                self.advance_level()
                
        return enemies_to_spawn
        
    def advance_level(self):
        """Move to the next level"""
        self.current_level_num += 1
        self.current_level = Level(self.current_level_num)
        
    def get_current_level(self):
        """Get the current level object"""
        return self.current_level
        
    def is_game_complete(self):
        """Check if all levels are complete"""
        return self.all_levels_complete
