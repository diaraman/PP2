import json
import os

class PersistenceManager:
    def __init__(self):
        # File-based storage keeps the app simple and avoids extra dependencies.
        self.settings_file = "settings.json"
        self.leaderboard_file = "leaderboard.json"
        self.default_settings = {
            "sound": True,
            "car_color": "green",
            "difficulty": "medium"
        }
        
    def load_settings(self):
        """Load settings from JSON file"""
        # Load the saved settings, but fall back to defaults if the file is missing or broken.
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    settings = json.load(f)
                    # Merge with defaults to ensure all keys exist
                    for key, value in self.default_settings.items():
                        if key not in settings:
                            settings[key] = value
                    return settings
            except (json.JSONDecodeError, IOError):
                return self.default_settings.copy()
        return self.default_settings.copy()
        
    def save_settings(self, settings):
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(settings, f, indent=4)
            return True
        except IOError:
            return False
            
    def load_leaderboard(self):
        """Load leaderboard from JSON file"""
        # Leaderboard entries are always sorted with the highest score first.
        if os.path.exists(self.leaderboard_file):
            try:
                with open(self.leaderboard_file, 'r') as f:
                    leaderboard = json.load(f)
                    if isinstance(leaderboard, list):
                        # Sort by score descending
                        return sorted(leaderboard, key=lambda x: x.get('score', 0), reverse=True)
            except (json.JSONDecodeError, IOError):
                pass
        return []
        
    def save_score(self, score_data):
        """Save a new score to leaderboard, keeping top 10"""
        # Append the new result, sort again, and keep only the best 10 runs.
        leaderboard = self.load_leaderboard()
        leaderboard.append(score_data)
        # Sort by score and keep top 10
        leaderboard = sorted(leaderboard, key=lambda x: x.get('score', 0), reverse=True)[:10]
        
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump(leaderboard, f, indent=4)
            return True
        except IOError:
            return False
            
    def clear_leaderboard(self):
        """Clear all leaderboard entries"""
        try:
            with open(self.leaderboard_file, 'w') as f:
                json.dump([], f)
            return True
        except IOError:
            return False
