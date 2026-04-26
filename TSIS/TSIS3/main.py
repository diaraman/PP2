import pygame
import sys
from racer import RacerGame
from ui import UIManager
from persistence import PersistenceManager

class Game:
    def __init__(self):
        # Pygame setup happens once at the top level of the app.
        pygame.init()
        pygame.mixer.init()
        
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("TSIS 3 - Advanced Racer Game")
        self.clock = pygame.time.Clock()
        
        # PersistenceManager handles settings and leaderboard files.
        self.persistence = PersistenceManager()
        self.settings = self.persistence.load_settings()
        self.leaderboard = self.persistence.load_leaderboard()
        
        self.ui_manager = UIManager(self.screen, self.settings)
        self.game = None
        self.current_screen = "menu"
        self.username = ""
        
    def run(self):
        # The game uses a simple screen-state loop instead of separate windows.
        running = True
        while running:
            if self.current_screen == "menu":
                result = self.ui_manager.main_menu()
                if result == "play":
                    # Ask for a username before starting the race.
                    self.username = self.ui_manager.get_username()
                    if self.username:
                        self.current_screen = "game"
                        self.game = RacerGame(self.screen, self.clock, self.settings, self.username)
                elif result == "leaderboard":
                    self.current_screen = "leaderboard"
                elif result == "settings":
                    self.current_screen = "settings"
                elif result == "quit":
                    running = False
                    
            elif self.current_screen == "game":
                result = self.game.run()
                if result:
                    # Save the score immediately after the run ends.
                    self.persistence.save_score(result)
                    self.leaderboard = self.persistence.load_leaderboard()
                self.current_screen = "game_over"
                
            elif self.current_screen == "game_over":
                score_data = self.game.get_score_data() if self.game else None
                action = self.ui_manager.game_over_screen(score_data)
                if action == "retry":
                    self.current_screen = "game"
                    self.game = RacerGame(self.screen, self.clock, self.settings, self.username)
                elif action == "menu":
                    self.current_screen = "menu"
                    
            elif self.current_screen == "leaderboard":
                if self.ui_manager.leaderboard_screen(self.leaderboard):
                    self.current_screen = "menu"
                    
            elif self.current_screen == "settings":
                new_settings = self.ui_manager.settings_screen(self.settings)
                if new_settings:
                    self.settings = new_settings
                    self.persistence.save_settings(self.settings)
                    self.ui_manager.settings = self.settings
                    self.current_screen = "menu"
                    
            pygame.display.flip()
            self.clock.tick(60)
            
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    game = Game()
    game.run()
