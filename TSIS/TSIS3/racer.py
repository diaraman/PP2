import pygame
import random
import math

class Player:
    def __init__(self, x, y, color=(0, 255, 0)):
        # The player's car stays in one of five lanes.
        self.x = x
        self.y = y
        self.width = 45
        self.height = 70
        self.color = color
        self.lane = 2
        self.lanes = [200, 300, 400, 500, 600]
        self.overtaking = False
        self.overtake_timer = 0
        
    def move(self, direction):
        if direction == "left" and self.lane > 0:
            self.lane -= 1
        elif direction == "right" and self.lane < 4:
            self.lane += 1
        self.x = self.lanes[self.lane]
        
    def start_overtake(self):
        # Overtaking is a short timed boost animation.
        if not self.overtaking:
            self.overtaking = True
            self.overtake_timer = 30
            
    def update(self):
        if self.overtaking:
            self.overtake_timer -= 1
            if self.overtake_timer <= 0:
                self.overtaking = False
                
    def draw(self, screen):
        if self.overtaking:
            body_color = (255, 100, 0)
        else:
            body_color = self.color
            
        pygame.draw.rect(screen, body_color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, (100, 100, 100), (self.x + 8, self.y - 5, self.width - 16, 15), border_radius=5)
        pygame.draw.rect(screen, (135, 206, 235), (self.x + 5, self.y + 10, 10, 20), border_radius=3)
        pygame.draw.rect(screen, (135, 206, 235), (self.x + self.width - 15, self.y + 10, 10, 20), border_radius=3)
        pygame.draw.rect(screen, (135, 206, 235), (self.x + self.width//2 - 8, self.y + 8, 16, 15), border_radius=3)
        pygame.draw.circle(screen, (255, 255, 200), (self.x + 5, self.y + self.height - 8), 5)
        pygame.draw.circle(screen, (255, 255, 200), (self.x + self.width - 5, self.y + self.height - 8), 5)
        pygame.draw.circle(screen, (255, 255, 100), (self.x + 5, self.y + 5), 4)
        pygame.draw.circle(screen, (255, 255, 100), (self.x + self.width - 5, self.y + 5), 4)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + 8, self.y + self.height - 8), 6)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + self.width - 8, self.y + self.height - 8), 6)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + 8, self.y + 5), 6)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + self.width - 8, self.y + 5), 6)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Coin:
    def __init__(self, x, y, value=1):
        # Coins have different values and are drawn as a simple animated pickup.
        self.x = x
        self.y = y
        self.width = 25
        self.height = 25
        self.value = value
        self.colors = {1: (205, 127, 50), 2: (192, 192, 192), 3: (255, 215, 0)}
        self.color = self.colors.get(value, (255, 215, 0))
        self.rotation = 0
        
    def draw(self, screen):
        self.rotation += 0.1
        size = 12 + abs(math.sin(self.rotation)) * 3
        pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), size)
        pygame.draw.circle(screen, (255, 255, 255), (self.x + self.width//2, self.y + self.height//2), size, 2)
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.value), True, (0, 0, 0))
        screen.blit(text, (self.x + 8, self.y + 5))
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class TrafficCar:
    def __init__(self, x, y, speed=3, color=None):
        # Traffic cars are obstacles that move down the road toward the player.
        self.x = x
        self.y = y
        self.width = 45
        self.height = 70
        self.speed = speed
        self.color = color or (random.randint(100, 200), 0, random.randint(100, 200))
        self.overtaking_from_right = False
        
    def update(self):
        self.y += self.speed
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height), border_radius=8)
        pygame.draw.rect(screen, (80, 80, 80), (self.x + 8, self.y - 5, self.width - 16, 15), border_radius=5)
        pygame.draw.rect(screen, (100, 100, 150), (self.x + 5, self.y + 10, 10, 20), border_radius=3)
        pygame.draw.rect(screen, (100, 100, 150), (self.x + self.width - 15, self.y + 10, 10, 20), border_radius=3)
        pygame.draw.circle(screen, (255, 100, 100), (self.x + 5, self.y + 5), 4)
        pygame.draw.circle(screen, (255, 100, 100), (self.x + self.width - 5, self.y + 5), 4)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + 8, self.y + self.height - 8), 6)
        pygame.draw.circle(screen, (30, 30, 30), (self.x + self.width - 8, self.y + self.height - 8), 6)
        
        if self.overtaking_from_right:
            pygame.draw.circle(screen, (255, 255, 0), (self.x + self.width + 5, self.y + self.height//2), 5)
        
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class Obstacle:
    def __init__(self, x, y, obstacle_type="barrier"):
        # Obstacles apply different damage and slowdown effects.
        self.x = x
        self.y = y
        self.width = 40
        self.height = 40
        self.type = obstacle_type
        self.animation = 0
        
        # Типы препятствий и их характеристики
        self.obstacle_data = {
            "barrier": {
                "color": (139, 69, 19),
                "damage": 50,
                "slow": 0.5,
                "name": "БАРЬЕР"
            },
            "oil": {
                "color": (50, 50, 50),
                "damage": 10,
                "slow": 0.4,
                "name": "МАСЛО"
            },
            "pothole": {
                "color": (80, 80, 80),
                "damage": 20,
                "slow": 0.6,
                "name": "ЯМА"
            },
            "cone": {
                "color": (255, 100, 0),
                "damage": 15,
                "slow": 0.7,
                "name": "КОНУС"
            },
            "tire": {
                "color": (40, 40, 40),
                "damage": 10,
                "slow": 0.5,
                "name": "ШИНА"
            },
            "water": {
                "color": (0, 100, 200),
                "damage": 5,
                "slow": 0.3,
                "name": "ЛУЖА"
            },
            "ice": {
                "color": (200, 230, 255),
                "damage": 5,
                "slow": 0.2,
                "name": "ЛЁД"
            },
            "sand": {
                "color": (194, 178, 128),
                "damage": 5,
                "slow": 0.35,
                "name": "ПЕСОК"
            },
            "hole": {
                "color": (60, 40, 20),
                "damage": 30,
                "slow": 0.4,
                "name": "ЯМА"
            },
            "spikes": {
                "color": (192, 192, 192),
                "damage": 40,
                "slow": 0.6,
                "name": "ШИПЫ"
            }
        }
        
        self.data = self.obstacle_data.get(obstacle_type, self.obstacle_data["barrier"])
        self.color = self.data["color"]
        self.damage = self.data["damage"]
        self.slow = self.data["slow"]
        self.name = self.data["name"]
            
    def update(self):
        self.animation += 0.1
        
    def draw(self, screen):
        self.update()
        
        if self.type == "barrier":
            # Барьер с предупреждением
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            pygame.draw.line(screen, (255, 0, 0), (self.x, self.y), (self.x + self.width, self.y + self.height), 4)
            pygame.draw.line(screen, (255, 0, 0), (self.x + self.width, self.y), (self.x, self.y + self.height), 4)
            # Мигающий красный свет
            if int(self.animation) % 2 == 0:
                pygame.draw.circle(screen, (255, 0, 0), (self.x + self.width//2, self.y + self.height//2), 5)
                
        elif self.type == "oil":
            # Масляное пятно
            for i in range(3):
                offset_x = math.sin(self.animation + i) * 3
                offset_y = math.cos(self.animation + i) * 2
                pygame.draw.ellipse(screen, self.color, 
                                   (self.x + offset_x, self.y + offset_y, self.width, self.height))
            pygame.draw.ellipse(screen, (100, 100, 100), 
                               (self.x + 5, self.y + 5, self.width - 10, self.height - 10))
                               
        elif self.type == "pothole":
            # Глубокая яма
            pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), 18)
            pygame.draw.circle(screen, (0, 0, 0), (self.x + self.width//2, self.y + self.height//2), 12)
            pygame.draw.circle(screen, (40, 40, 40), (self.x + self.width//2, self.y + self.height//2), 8)
            
        elif self.type == "cone":
            # Дорожный конус
            points = [(self.x + self.width//2, self.y),
                     (self.x + 5, self.y + self.height - 5),
                     (self.x + self.width - 5, self.y + self.height - 5)]
            pygame.draw.polygon(screen, self.color, points)
            pygame.draw.rect(screen, (255, 255, 255), 
                            (self.x + self.width//2 - 5, self.y + self.height - 15, 10, 10))
                            
        elif self.type == "tire":
            # Покрышка
            pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), 15)
            pygame.draw.circle(screen, (20, 20, 20), (self.x + self.width//2, self.y + self.height//2), 8)
            for i in range(4):
                angle = self.animation + i * math.pi/2
                x_offset = math.cos(angle) * 12
                y_offset = math.sin(angle) * 12
                pygame.draw.line(screen, (80, 80, 80),
                               (self.x + self.width//2, self.y + self.height//2),
                               (self.x + self.width//2 + x_offset, self.y + self.height//2 + y_offset), 2)
                               
        elif self.type == "water":
            # Лужа с эффектом
            for i in range(3):
                ripple = math.sin(self.animation * 5 + i) * 2
                pygame.draw.ellipse(screen, self.color,
                                   (self.x + i*ripple, self.y + i*ripple/2, 
                                    self.width - i*ripple*2, self.height - i*ripple))
            pygame.draw.ellipse(screen, (150, 200, 255), 
                               (self.x + 5, self.y + 5, self.width - 10, self.height - 10), 2)
                               
        elif self.type == "ice":
            # Ледяной участок
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            for i in range(3):
                pygame.draw.line(screen, (255, 255, 255),
                               (self.x + 5 + i*10, self.y),
                               (self.x + 15 + i*10, self.y + self.height), 2)
                               
        elif self.type == "sand":
            # Песок
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            for i in range(5):
                pygame.draw.circle(screen, (220, 200, 150),
                                 (self.x + random.randint(5, self.width-5),
                                  self.y + random.randint(5, self.height-5)), 3)
                                 
        elif self.type == "hole":
            # Открытый люк
            pygame.draw.circle(screen, self.color, (self.x + self.width//2, self.y + self.height//2), 18)
            pygame.draw.circle(screen, (0, 0, 0), (self.x + self.width//2, self.y + self.height//2), 14)
            pygame.draw.line(screen, (255, 0, 0),
                           (self.x + self.width//2 - 10, self.y + self.height//2),
                           (self.x + self.width//2 + 10, self.y + self.height//2), 3)
                           
        elif self.type == "spikes":
            # Шипы
            pygame.draw.rect(screen, self.color, (self.x, self.y, self.width, self.height))
            for i in range(5):
                pygame.draw.polygon(screen, (150, 150, 150),
                                  [(self.x + i*8, self.y + self.height),
                                   (self.x + i*8 + 4, self.y + self.height - 10),
                                   (self.x + i*8 + 8, self.y + self.height)])
                                  
        # Отображение иконки опасности
        if self.damage > 20:
            font = pygame.font.Font(None, 16)
            text = font.render("!", True, (255, 0, 0))
            screen.blit(text, (self.x + self.width//2 - 4, self.y + 5))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class PowerUp:
    def __init__(self, x, y, power_type):
        # Power-ups are temporary pickups that change the player's state.
        self.x = x
        self.y = y
        self.width = 30
        self.height = 30
        self.type = power_type
        self.lifetime = 450
        if power_type == "nitro":
            self.color = (0, 255, 255)
        elif power_type == "shield":
            self.color = (0, 0, 255)
        elif power_type == "repair":
            self.color = (0, 255, 0)
        self.animation_frame = 0
            
    def update(self):
        self.lifetime -= 1
        self.animation_frame += 1
        return self.lifetime > 0
        
    def draw(self, screen):
        size_offset = abs(math.sin(self.animation_frame * 0.1)) * 3
        draw_x = self.x - size_offset / 2
        draw_y = self.y - size_offset / 2
        draw_size = self.width + size_offset
        
        pygame.draw.rect(screen, self.color, (draw_x, draw_y, draw_size, draw_size), border_radius=5)
        pygame.draw.rect(screen, (255, 255, 255), (draw_x, draw_y, draw_size, draw_size), 2, border_radius=5)
        
        font = pygame.font.Font(None, 20)
        if self.type == "nitro":
            text = font.render("N", True, (255, 255, 255))
        elif self.type == "shield":
            text = font.render("S", True, (255, 255, 255))
        else:
            text = font.render("R", True, (255, 255, 255))
        screen.blit(text, (self.x + 10, self.y + 5))
            
    def get_rect(self):
        return pygame.Rect(self.x, self.y, self.width, self.height)

class RoadEvent:
    def __init__(self, event_type, lane, duration=180):
        self.type = event_type
        self.lane = lane
        self.duration = duration
        self.active = True
        
    def update(self):
        self.duration -= 1
        if self.duration <= 0:
            self.active = False
            
    def draw(self, screen, lane_x):
        if self.type == "nitro_strip":
            color = (0, 255, 255)
            pygame.draw.rect(screen, color, (lane_x, 570, 45, 30))
            for i in range(3):
                pygame.draw.line(screen, (255, 255, 255), 
                               (lane_x + 5 + i*12, 575), 
                               (lane_x + 15 + i*12, 595), 2)
        elif self.type == "speed_bump":
            pygame.draw.rect(screen, (139, 69, 19), (lane_x, 570, 45, 15))
            pygame.draw.line(screen, (255, 255, 0), (lane_x, 570), (lane_x + 45, 570), 2)

class RacerGame:
    def __init__(self, screen, clock, settings, username):
        # RacerGame owns the actual race loop and all gameplay objects.
        self.screen = screen
        self.clock = clock
        self.settings = settings
        self.username = username
        
        self.road_width = 450
        self.road_x = 175
        
        self.player = Player(400, 500, self.get_car_color())
        
        self.coins = []
        self.traffic = []
        self.obstacles = []
        self.powerups = []
        self.road_events = []
        
        self.score = 0
        self.coins_collected = 0
        self.distance = 0
        self.target_distance = 5000
        self.speed = 5
        self.base_speed = 5
        
        self.active_powerup = None
        self.powerup_timer = 0
        self.shield_active = False
        self.nitro_multiplier = 1.0
        
        self.difficulty_settings = {
            "easy": {"speed_base": 4, "spawn_multiplier": 0.6, "traffic_multiplier": 0.7},
            "medium": {"speed_base": 5, "spawn_multiplier": 1.0, "traffic_multiplier": 1.0},
            "hard": {"speed_base": 7, "spawn_multiplier": 1.5, "traffic_multiplier": 1.3}
        }
        current_difficulty = settings.get("difficulty", "medium")
        self.difficulty_config = self.difficulty_settings[current_difficulty]
        self.base_speed = self.difficulty_config["speed_base"]
        self.speed = self.base_speed
        
        self.spawn_timer = 0
        self.game_over = False
        self.paused = False
        self.overtake_cooldown = 0
        
        self.font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        self.large_font = pygame.font.Font(None, 72)
        
        self.sound_enabled = settings.get("sound", True)
        
        # Список всех возможных препятствий
        self.obstacle_types = ["barrier", "oil", "pothole", "cone", "tire", "water", "ice", "sand", "hole", "spikes"]
        
    def get_car_color(self):
        colors = {
            "red": (220, 50, 50),
            "green": (50, 220, 50),
            "blue": (50, 50, 220),
            "yellow": (220, 220, 50),
            "purple": (160, 50, 220)
        }
        return colors.get(self.settings.get("car_color", "green"), (50, 220, 50))
        
    def perform_overtake(self):
        if self.overtake_cooldown <= 0 and not self.player.overtaking:
            self.player.start_overtake()
            self.overtake_cooldown = 120
            self.score += 25
            self.speed = self.base_speed * 1.5
            return True
        return False
        
    def spawn_traffic_with_overtake(self):
        lane = random.randint(0, 4)
        x = self.player.lanes[lane]
        speed = random.uniform(3, 6) * self.difficulty_config["traffic_multiplier"]
        traffic_car = TrafficCar(x, -60, speed)
        if random.random() < 0.2:
            traffic_car.overtaking_from_right = True
        self.traffic.append(traffic_car)
        
    def update_overtaking(self):
        self.player.update()
        if self.overtake_cooldown > 0:
            self.overtake_cooldown -= 1
        if not self.player.overtaking and self.active_powerup != "nitro":
            self.speed = self.base_speed
        for traffic in self.traffic:
            if traffic.overtaking_from_right and traffic.y > 200:
                if traffic.x < self.player.lanes[4] - 50:
                    traffic.x += 2
                    
    def spawn_coin(self):
        lane = random.randint(0, 4)
        x = self.player.lanes[lane]
        rand = random.random()
        if rand < 0.6:
            value = 1
        elif rand < 0.9:
            value = 2
        else:
            value = 3
        self.coins.append(Coin(x, -30, value))
        
    def spawn_traffic(self):
        available_lanes = [i for i in range(5) if i != self.player.lane]
        if not available_lanes:
            available_lanes = [self.player.lane]
        lane = random.choice(available_lanes)
        x = self.player.lanes[lane]
        speed = random.uniform(3, 6) * self.difficulty_config["traffic_multiplier"]
        self.traffic.append(TrafficCar(x, -60, speed))
        
    def spawn_obstacle(self):
        """Спавн разнообразных препятствий с весами"""
        # Spawn obstacles less frequently when they are more dangerous.
        if random.random() < 0.35:  # Увеличил шанс спавна
            lane = random.randint(0, 4)
            x = self.player.lanes[lane]
            
            # Веса для разных типов препятствий (чем опаснее, тем реже)
            weights = [0.15, 0.2, 0.1, 0.1, 0.1, 0.1, 0.05, 0.05, 0.05, 0.1]
            obstacle_type = random.choices(self.obstacle_types, weights)[0]
            self.obstacles.append(Obstacle(x, -40, obstacle_type))
        
    def spawn_powerup(self):
        if len(self.powerups) < 2:
            lane = random.randint(0, 4)
            x = self.player.lanes[lane]
            power_types = ["nitro", "shield", "repair"]
            power_type = random.choice(power_types)
            self.powerups.append(PowerUp(x, -40, power_type))
            
    def spawn_road_event(self):
        if random.random() < 0.015:
            lane = random.randint(0, 4)
            event_types = ["nitro_strip", "speed_bump"]
            event_type = random.choice(event_types)
            self.road_events.append(RoadEvent(event_type, lane))
            
    def update_powerup(self):
        if self.active_powerup:
            if self.active_powerup == "shield":
                return
            self.powerup_timer -= 1
            if self.powerup_timer <= 0:
                if self.active_powerup == "nitro":
                    self.speed = self.base_speed
                    self.nitro_multiplier = 1.0
                self.active_powerup = None
                
    def apply_powerup(self, powerup):
        if self.active_powerup:
            return
            
        if powerup.type == "nitro":
            self.active_powerup = "nitro"
            self.powerup_timer = 240
            self.nitro_multiplier = 2.0
            self.speed = self.base_speed * self.nitro_multiplier
            self.score += 50
            self.message = "Picked up Nitro"
            
        elif powerup.type == "shield":
            self.active_powerup = "shield"
            self.powerup_timer = -1
            self.shield_active = True
            self.score += 30
            self.message = "Picked up Shield"
            
        elif powerup.type == "repair":
            if self.obstacles:
                # Remove the obstacle closest to the player so repair feels immediate.
                closest_obstacle = max(self.obstacles, key=lambda item: item.y)
                self.obstacles.remove(closest_obstacle)
                self.score += 20
            self.speed = self.base_speed * self.nitro_multiplier
            self.message = "Picked up Repair"
            
    def check_collisions(self):
        player_rect = self.player.get_rect()

        # Check traffic, obstacles, coins, power-ups, and road events one by one.
        for traffic in self.traffic[:]:
            if player_rect.colliderect(traffic.get_rect()):
                if traffic.overtaking_from_right:
                    if self.player.overtaking:
                        self.score += 100
                        self.traffic.remove(traffic)
                        continue
                if not self.shield_active:
                    return True
                # Shield absorbs the hit, removes the car, and is consumed.
                self.traffic.remove(traffic)
                self.shield_active = False
                self.active_powerup = None
                self.powerup_timer = 0
                self.score -= 20
                    
        for obstacle in self.obstacles[:]:
            if player_rect.colliderect(obstacle.get_rect()):
                if self.shield_active:
                    # Shield blocks the obstacle completely and is consumed.
                    self.obstacles.remove(obstacle)
                    self.shield_active = False
                    self.active_powerup = None
                    self.powerup_timer = 0
                    self.score += 5
                    continue

                # Apply the normal obstacle effects when no shield is active.
                self.score -= obstacle.damage
                self.speed = max(2, self.speed * obstacle.slow)

                # Extra effects for special obstacles.
                if obstacle.type == "ice":
                    self.speed = max(1, self.speed * 0.5)  # Ice slows you down hard
                elif obstacle.type == "spikes":
                    return True  # Spikes can end the run
                elif obstacle.type == "hole":
                    self.score -= 50  # Hole causes extra damage

                self.obstacles.remove(obstacle)
                
        for coin in self.coins[:]:
            if player_rect.colliderect(coin.get_rect()):
                self.coins_collected += 1
                points = coin.value * 10
                self.score += points
                self.coins.remove(coin)
                
        for powerup in self.powerups[:]:
            if player_rect.colliderect(powerup.get_rect()):
                self.apply_powerup(powerup)
                self.powerups.remove(powerup)
                
        for event in self.road_events[:]:
            if event.lane == self.player.lane and event.active:
                if event.type == "nitro_strip":
                    self.speed = min(self.base_speed * 2.5, self.speed * 1.5)
                    event.active = False
                elif event.type == "speed_bump":
                    self.speed = max(2, self.speed * 0.7)
                    event.active = False
                    
        return False
        
    def update_difficulty(self):
        progress = self.distance / self.target_distance
        speed_increase = progress * 3
        self.base_speed = self.difficulty_config["speed_base"] + speed_increase
        
        if self.active_powerup != "nitro" and not self.player.overtaking:
            self.speed = self.base_speed
        elif self.player.overtaking:
            self.speed = self.base_speed * 1.5
        else:
            self.speed = self.base_speed * 2.0
            
        return min(2.0, 0.5 + progress * 1.5)
        
    def update(self):
        if self.game_over or self.paused:
            return
            
        self.distance += self.speed / 10
        if self.distance >= self.target_distance:
            self.game_over = True
            self.score += 1000
            return
            
        self.update_powerup()
        self.update_overtaking()
        
        spawn_multiplier = self.update_difficulty() * self.difficulty_config["spawn_multiplier"]
        
        self.spawn_timer += 1
        spawn_interval = max(20, 50 - int(self.distance / 100))
        
        if self.spawn_timer > spawn_interval:
            self.spawn_timer = 0
            
            if random.random() < 0.4 * spawn_multiplier:
                self.spawn_traffic()
                
            if random.random() < 0.35 * spawn_multiplier:  # Увеличил частоту препятствий
                self.spawn_obstacle()
                
            if random.random() < 0.35:
                self.spawn_coin()
                
            if random.random() < 0.04 * spawn_multiplier:
                self.spawn_powerup()
                
            self.spawn_road_event()
            
        for traffic in self.traffic[:]:
            traffic.update()
            if traffic.y > 600:
                self.traffic.remove(traffic)
                
        for obstacle in self.obstacles[:]:
            obstacle.y += self.speed
            if obstacle.y > 600:
                self.obstacles.remove(obstacle)
                
        for coin in self.coins[:]:
            coin.y += self.speed
            if coin.y > 600:
                self.coins.remove(coin)
                
        for powerup in self.powerups[:]:
            if not powerup.update():
                self.powerups.remove(powerup)
            else:
                powerup.y += self.speed
                if powerup.y > 600:
                    self.powerups.remove(powerup)
                    
        for event in self.road_events[:]:
            event.update()
            if not event.active:
                self.road_events.remove(event)
                
        if self.check_collisions():
            self.game_over = True
            
        self.score += int(self.speed / 10)
        
    def draw(self):
        self.screen.fill((30, 40, 60))
        pygame.draw.rect(self.screen, (50, 50, 50), (self.road_x, 0, self.road_width, 600))
        
        for i in range(1, 5):
            x = self.road_x + i * 90
            for y in range(0, 600, 50):
                pygame.draw.rect(self.screen, (255, 255, 255), (x - 3, y + (pygame.time.get_ticks() % 100), 6, 30))
                
        pygame.draw.line(self.screen, (255, 255, 0), (self.road_x, 0), (self.road_x, 600), 4)
        pygame.draw.line(self.screen, (255, 255, 0), (self.road_x + self.road_width, 0), 
                        (self.road_x + self.road_width, 600), 4)
                        
        for i in range(0, 2):
            side_x = self.road_x - 20 + i * (self.road_width + 40)
            for y in range(0, 600, 60):
                pygame.draw.rect(self.screen, (255, 255, 255), (side_x, y, 10, 30))
        
        for event in self.road_events:
            if event.active:
                event.draw(self.screen, self.player.lanes[event.lane])
                
        for obstacle in self.obstacles:
            obstacle.draw(self.screen)
        for powerup in self.powerups:
            powerup.draw(self.screen)
        for coin in self.coins:
            coin.draw(self.screen)
        for traffic in self.traffic:
            traffic.draw(self.screen)
            
        self.player.draw(self.screen)
        
        if self.shield_active:
            shield_surf = pygame.Surface((self.player.width + 10, self.player.height + 10), pygame.SRCALPHA)
            pygame.draw.ellipse(shield_surf, (0, 0, 255, 100), (0, 0, self.player.width + 10, self.player.height + 10))
            self.screen.blit(shield_surf, (self.player.x - 5, self.player.y - 5))
            
        self.draw_ui()
        
    def draw_ui(self):
        score_panel = pygame.Surface((220, 200))
        score_panel.set_alpha(200)
        score_panel.fill((0, 0, 0))
        self.screen.blit(score_panel, (10, 10))
        
        score_text = self.font.render(f"Score: {self.score}", True, (255, 255, 255))
        self.screen.blit(score_text, (20, 20))
        
        coins_text = self.font.render(f"Coins: {self.coins_collected}", True, (255, 215, 0))
        self.screen.blit(coins_text, (20, 55))
        
        distance_text = self.small_font.render(f"Distance: {int(self.distance)}/{self.target_distance}", True, (255, 255, 255))
        self.screen.blit(distance_text, (20, 90))
        
        progress_width = int((self.distance / self.target_distance) * 200)
        pygame.draw.rect(self.screen, (100, 100, 100), (20, 115, 200, 15))
        pygame.draw.rect(self.screen, (0, 255, 0), (20, 115, progress_width, 15))
        
        speed_text = self.small_font.render(f"Speed: {int(self.speed * 15)} km/h", True, (255, 255, 255))
        self.screen.blit(speed_text, (20, 145))
        
        if self.overtake_cooldown > 0:
            overtake_text = self.small_font.render(f"Overtake: {self.overtake_cooldown//60}s", True, (255, 165, 0))
            self.screen.blit(overtake_text, (20, 175))
        else:
            overtake_text = self.small_font.render("Press SPACE to overtake!", True, (0, 255, 0))
            self.screen.blit(overtake_text, (20, 175))
        
        if self.active_powerup:
            powerup_panel = pygame.Surface((220, 60))
            powerup_panel.set_alpha(200)
            powerup_panel.fill((0, 0, 0))
            self.screen.blit(powerup_panel, (10, 210))
            
            powerup_name_map = {
                "nitro": "NITRO",
                "shield": "SHIELD",
                "repair": "REPAIR",
            }
            powerup_name = powerup_name_map.get(self.active_powerup, self.active_powerup.upper())
            powerup_text = self.small_font.render(f"{powerup_name}", True, (0, 255, 0))
            self.screen.blit(powerup_text, (20, 220))

            if self.active_powerup == "shield":
                timer_text = self.small_font.render("Until hit", True, (255, 255, 255))
            else:
                timer_text = self.small_font.render(f"Time: {self.powerup_timer//60}s", True, (255, 255, 255))
            self.screen.blit(timer_text, (20, 245))
            
        instr_text = self.small_font.render("← → Move | SPACE Overtake | ESC Pause", True, (200, 200, 200))
        self.screen.blit(instr_text, (20, 570))
        
        # Счетчик препятствий
        obstacle_count = self.small_font.render(f"Obstacles: {len(self.obstacles)}", True, (255, 100, 100))
        self.screen.blit(obstacle_count, (20, 280))
        
    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    self.player.move("left")
                elif event.key == pygame.K_RIGHT:
                    self.player.move("right")
                elif event.key == pygame.K_SPACE:
                    self.perform_overtake()
                elif event.key == pygame.K_ESCAPE:
                    self.paused = not self.paused
        return True
        
    def get_score_data(self):
        return {
            "username": self.username,
            "score": self.score,
            "distance": int(self.distance),
            "coins": self.coins_collected
        }
        
    def run(self):
        running = True
        while running and not self.game_over:
            if not self.paused:
                running = self.handle_events()
                self.update()
                self.draw()
            else:
                self.draw()
                pause_text = self.large_font.render("PAUSED", True, (255, 255, 255))
                pause_rect = pause_text.get_rect(center=(400, 300))
                self.screen.blit(pause_text, pause_rect)
                pygame.display.flip()
                self.clock.tick(60)
                
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return None
                    if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                        self.paused = False
                        
            pygame.display.flip()
            self.clock.tick(60)
            
        if self.game_over:
            return self.get_score_data()
        return None
