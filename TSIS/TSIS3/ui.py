import pygame
import sys

class Button:
    def __init__(self, x, y, width, height, text, color=(70, 70, 70), hover_color=(120, 120, 120)):
        # A button is just a rectangle plus a label and hover behavior.
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.current_color = color
        self.font = pygame.font.Font(None, 32)
        
    def draw(self, screen):
        pygame.draw.rect(screen, self.current_color, self.rect)
        pygame.draw.rect(screen, (255, 255, 255), self.rect, 3)
        text_surface = self.font.render(self.text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)
        
    def handle_event(self, event):
        if event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos):
                self.current_color = self.hover_color
            else:
                self.current_color = self.color
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                return True
        return False

class UIManager:
    def __init__(self, screen, settings):
        # UIManager owns every menu and screen outside the actual race loop.
        self.screen = screen
        self.settings = settings
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 32)
        self.title_font = pygame.font.Font(None, 72)
        self.username_input = ""
        self.input_active = False
        
    def draw_background(self):
        """Draw gradient background"""
        for i in range(600):
            color_value = 50 + int(i / 600 * 100)
            pygame.draw.line(self.screen, (color_value, color_value, color_value + 50), 
                           (0, i), (800, i))
            
    def main_menu(self):
        # Show the main menu until the player chooses an action.
        buttons = [
            Button(300, 250, 200, 60, "PLAY"),
            Button(300, 330, 200, 60, "LEADERBOARD"),
            Button(300, 410, 200, 60, "SETTINGS"),
            Button(300, 490, 200, 60, "QUIT")
        ]
        
        while True:
            self.draw_background()
            
            # Title with animation
            title = self.title_font.render("TSIS 3 RACER", True, (255, 215, 0))
            title_shadow = self.title_font.render("TSIS 3 RACER", True, (100, 100, 0))
            title_rect = title.get_rect(center=(400, 120))
            self.screen.blit(title_shadow, (title_rect.x + 3, title_rect.y + 3))
            self.screen.blit(title, title_rect)
            
            # Subtitle
            subtitle = self.small_font.render("Advanced Racing Game", True, (200, 200, 200))
            subtitle_rect = subtitle.get_rect(center=(400, 180))
            self.screen.blit(subtitle, subtitle_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "quit"
                for button in buttons:
                    if button.handle_event(event):
                        if button.text == "PLAY":
                            return "play"
                        elif button.text == "LEADERBOARD":
                            return "leaderboard"
                        elif button.text == "SETTINGS":
                            return "settings"
                        elif button.text == "QUIT":
                            return "quit"
                            
            for button in buttons:
                button.draw(self.screen)
                
            pygame.display.flip()
            
    def get_username(self):
        # This screen collects keyboard input one character at a time.
        input_box = pygame.Rect(250, 300, 300, 50)
        self.username_input = ""
        self.input_active = True
        
        while self.input_active:
            self.draw_background()
            
            title = self.font.render("ENTER YOUR NAME", True, (255, 255, 255))
            title_rect = title.get_rect(center=(400, 150))
            self.screen.blit(title, title_rect)
            
            # Draw input box
            pygame.draw.rect(self.screen, (255, 255, 255), input_box, 2)
            pygame.draw.rect(self.screen, (50, 50, 50), input_box)
            
            text_surface = self.small_font.render(self.username_input, True, (255, 255, 255))
            self.screen.blit(text_surface, (input_box.x + 10, input_box.y + 12))
            
            # Blinking cursor
            if pygame.time.get_ticks() % 1000 < 500:
                cursor_x = input_box.x + 10 + text_surface.get_width()
                pygame.draw.line(self.screen, (255, 255, 255), 
                               (cursor_x, input_box.y + 10), 
                               (cursor_x, input_box.y + 40), 2)
                
            # Instructions
            instr = self.small_font.render("Press ENTER to start | ESC to cancel", True, (150, 150, 150))
            instr_rect = instr.get_rect(center=(400, 400))
            self.screen.blit(instr, instr_rect)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.input_active = False
                    return None
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        if self.username_input.strip():
                            self.input_active = False
                            return self.username_input.strip()
                    elif event.key == pygame.K_ESCAPE:
                        self.input_active = False
                        return None
                    elif event.key == pygame.K_BACKSPACE:
                        self.username_input = self.username_input[:-1]
                    else:
                        if len(self.username_input) < 20 and event.unicode.isprintable():
                            self.username_input += event.unicode
                            
            pygame.display.flip()
            
        return "Player"
        
    def game_over_screen(self, score_data):
        # Show the final result and let the player retry or go back to the menu.
        buttons = [
            Button(250, 450, 130, 50, "RETRY"),
            Button(420, 450, 130, 50, "MENU")
        ]
        
        while True:
            self.draw_background()
            
            # Game over title with animation
            title = self.font.render("GAME OVER", True, (255, 0, 0))
            title_rect = title.get_rect(center=(400, 100))
            self.screen.blit(title, title_rect)
            
            if score_data:
                # Score panel
                panel = pygame.Surface((400, 250))
                panel.set_alpha(200)
                panel.fill((0, 0, 0))
                self.screen.blit(panel, (200, 150))
                
                stats = [
                    f"PLAYER: {score_data['username']}",
                    f"SCORE: {score_data['score']}",
                    f"DISTANCE: {score_data['distance']}m",
                    f"COINS: {score_data['coins']}"
                ]
                
                y_offset = 170
                for stat in stats:
                    text = self.small_font.render(stat, True, (255, 255, 255))
                    text_rect = text.get_rect(center=(400, y_offset))
                    self.screen.blit(text, text_rect)
                    y_offset += 50
                    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return "menu"
                for button in buttons:
                    if button.handle_event(event):
                        if button.text == "RETRY":
                            return "retry"
                        elif button.text == "MENU":
                            return "menu"
                            
            for button in buttons:
                button.draw(self.screen)
                
            pygame.display.flip()
            
    def leaderboard_screen(self, leaderboard):
        # Display the stored top scores in a simple table layout.
        back_button = Button(300, 520, 200, 50, "BACK")
        
        while True:
            self.draw_background()
            
            title = self.font.render("TOP 10 LEADERBOARD", True, (255, 215, 0))
            title_rect = title.get_rect(center=(400, 50))
            self.screen.blit(title, title_rect)
            
            # Headers
            headers = ["RANK", "NAME", "SCORE", "DISTANCE"]
            header_x = [70, 170, 390, 560]
            for i, header in enumerate(headers):
                header_text = self.small_font.render(header, True, (255, 255, 0))
                self.screen.blit(header_text, (header_x[i], 100))
                
            # Draw separator
            pygame.draw.line(self.screen, (255, 255, 255), (40, 130), (760, 130), 2)
            
            y_offset = 150
            for idx, entry in enumerate(leaderboard[:10]):
                # Alternate row colors
                color = (200, 200, 200) if idx % 2 == 0 else (150, 150, 150)
                
                rank_text = self.small_font.render(str(idx + 1), True, color)
                name_text = self.small_font.render(entry.get('username', 'Unknown')[:15], True, color)
                score_text = self.small_font.render(str(entry.get('score', 0)), True, color)
                dist_text = self.small_font.render(str(entry.get('distance', 0)), True, color)
                
                self.screen.blit(rank_text, (80, y_offset))
                self.screen.blit(name_text, (170, y_offset))
                self.screen.blit(score_text, (400, y_offset))
                self.screen.blit(dist_text, (570, y_offset))
                
                y_offset += 35
                if y_offset > 480:
                    break
                    
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return True
                if back_button.handle_event(event):
                    return True
                    
            back_button.draw(self.screen)
            pygame.display.flip()
            
    def settings_screen(self, current_settings):
        # Settings are edited in memory and returned to the caller when saved.
        # Create interactive buttons for settings
        sound_button = Button(300, 200, 200, 50, 
                             f"SOUND: {'ON' if current_settings.get('sound', True) else 'OFF'}")
        
        # Car color selector
        color_buttons = []
        colors = ["red", "green", "blue", "yellow", "purple"]
        color_display = {"red": (255, 50, 50), "green": (50, 255, 50), 
                        "blue": (50, 50, 255), "yellow": (255, 255, 50), 
                        "purple": (255, 50, 255)}
        
        for i, color in enumerate(colors):
            btn = Button(150 + i * 100, 300, 80, 50, color.capitalize()[:3], 
                        color_display[color], color_display[color])
            color_buttons.append((btn, color))
            
        # Difficulty selector
        difficulty_buttons = []
        difficulties = ["easy", "medium", "hard"]
        for i, diff in enumerate(difficulties):
            btn = Button(200 + i * 130, 400, 110, 50, diff.upper())
            difficulty_buttons.append((btn, diff))
            
        save_button = Button(300, 490, 200, 50, "SAVE & RETURN")
        
        while True:
            self.draw_background()
            
            title = self.font.render("SETTINGS", True, (255, 255, 255))
            title_rect = title.get_rect(center=(400, 80))
            self.screen.blit(title, title_rect)
            
            # Labels
            sound_label = self.small_font.render("Audio Settings:", True, (200, 200, 200))
            self.screen.blit(sound_label, (250, 170))
            
            car_label = self.small_font.render("Car Color:", True, (200, 200, 200))
            self.screen.blit(car_label, (250, 270))
            
            diff_label = self.small_font.render("Difficulty:", True, (200, 200, 200))
            self.screen.blit(diff_label, (250, 370))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return current_settings
                    
                if sound_button.handle_event(event):
                    current_settings['sound'] = not current_settings.get('sound', True)
                    sound_button.text = f"SOUND: {'ON' if current_settings['sound'] else 'OFF'}"
                    
                for btn, color in color_buttons:
                    if btn.handle_event(event):
                        current_settings['car_color'] = color
                        
                for btn, diff in difficulty_buttons:
                    if btn.handle_event(event):
                        current_settings['difficulty'] = diff
                        
                if save_button.handle_event(event):
                    return current_settings
                    
            sound_button.draw(self.screen)
            for btn, _ in color_buttons:
                btn.draw(self.screen)
            for btn, _ in difficulty_buttons:
                btn.draw(self.screen)
            save_button.draw(self.screen)
            
            # Highlight current selections
            pygame.draw.rect(self.screen, (0, 255, 0), 
                           (sound_button.rect.x - 3, sound_button.rect.y - 3, 
                            sound_button.rect.width + 6, sound_button.rect.height + 6), 3)
            
            for btn, color in color_buttons:
                if current_settings.get('car_color') == color:
                    pygame.draw.rect(self.screen, (0, 255, 0), 
                                   (btn.rect.x - 3, btn.rect.y - 3, 
                                    btn.rect.width + 6, btn.rect.height + 6), 3)
                    
            for btn, diff in difficulty_buttons:
                if current_settings.get('difficulty') == diff:
                    pygame.draw.rect(self.screen, (0, 255, 0), 
                                   (btn.rect.x - 3, btn.rect.y - 3, 
                                    btn.rect.width + 6, btn.rect.height + 6), 3)
                    
            pygame.display.flip()
