import os
import pygame


class MusicPlayer:
    def __init__(self, screen):
        # Pygame screen where we draw all UI text/panels
        self.screen = screen
        self.width, self.height = self.screen.get_size()

        # Folder that stores audio files
        self.music_folder = "music_player/music"
        # List of track file paths in the playlist
        self.playlist = self.load_playlist()
        # Which track is currently selected in playlist
        self.current_index = 0
        # Simple flag to show Play/Stop status in UI
        self.is_playing = False

        # Fonts used to draw text
        self.font_title = pygame.font.SysFont("arial", 36, bold=True)
        self.font_text = pygame.font.SysFont("arial", 24)
        self.font_small = pygame.font.SysFont("arial", 20)

    def load_playlist(self):
        # We build and return this list
        songs = []

        # If folder does not exist, return empty playlist (no crash)
        if not os.path.exists(self.music_folder):
            return songs

        # Read all file names from music folder in sorted order
        for file_name in sorted(os.listdir(self.music_folder)):
            # Keep only supported audio file formats
            if file_name.lower().endswith((".mp3", ".wav", ".ogg")):
                # Build full path: folder + file name
                full_path = os.path.join(self.music_folder, file_name)
                # Add only real files with size > 0 bytes
                if os.path.isfile(full_path) and os.path.getsize(full_path) > 0:
                    songs.append(full_path)

        return songs

    def reload_playlist(self):
        # Remember current play state so we can continue if needed
        was_playing = self.is_playing
        # Scan folder again and refresh track list
        self.playlist = self.load_playlist()

        # If no tracks after reload -> reset and stop player
        if len(self.playlist) == 0:
            self.current_index = 0
            self.stop()
            return

        # If current index is out of range, jump to first track
        if self.current_index >= len(self.playlist):
            self.current_index = 0

        # If music was playing before reload, start playing again
        if was_playing:
            self.play()

    def get_track_name(self):
        # Friendly fallback for UI when playlist is empty
        if len(self.playlist) == 0:
            return "No track"

        # Extract only file name from full path
        path = self.playlist[self.current_index]
        return os.path.basename(path)

    def play(self):
        # Nothing to play if playlist is empty
        if len(self.playlist) == 0:
            return

        track_path = self.playlist[self.current_index]

        try:
            # Load selected track and start playback
            pygame.mixer.music.load(track_path)
            pygame.mixer.music.play()
            self.is_playing = True
        except pygame.error:
            # If file cannot be decoded/played, mark as not playing
            self.is_playing = False

    def stop(self):
        # Stop current music immediately
        pygame.mixer.music.stop()
        self.is_playing = False

    def next_track(self):
        # Ignore if there are no tracks
        if len(self.playlist) == 0:
            return

        # Move to next track, wrap to start when we reach the end
        self.current_index = (self.current_index + 1) % len(self.playlist)
        self.play()

    def previous_track(self):
        # Ignore if there are no tracks
        if len(self.playlist) == 0:
            return

        # Move to previous track, wrap to last when we go below 0
        self.current_index = (self.current_index - 1) % len(self.playlist)
        self.play()

    def update_auto_next(self):
        # If current track finished, automatically switch to next
        if self.is_playing and not pygame.mixer.music.get_busy() and len(self.playlist) > 0:
            self.next_track()

    def get_position_seconds(self):
        # When stopped, progress is 0
        if not self.is_playing:
            return 0.0

        # Current playback position in milliseconds
        pos_ms = pygame.mixer.music.get_pos()
        # -1 means unknown position
        if pos_ms < 0:
            return 0.0

        # Convert milliseconds -> seconds
        return pos_ms / 1000.0

    def draw_text(self, text, x, y, font, color=(240, 244, 248)):
        # Render text surface and draw it on the screen
        text_surface = font.render(text, True, color)
        self.screen.blit(text_surface, (x, y))

    def draw(self, message=""):
        # Draw background and main panel
        self.screen.fill((25, 29, 35))
        pygame.draw.rect(self.screen, (38, 45, 55), (30, 30, self.width - 60, self.height - 60), border_radius=16)

        # Title
        self.draw_text("Music Player", 55, 48, self.font_title, (90, 188, 255))

        # If playlist is empty, show instruction text
        if len(self.playlist) == 0:
            self.draw_text("No tracks found in music_player/music", 55, 120, self.font_text)
            self.draw_text("Put .mp3/.wav/.ogg files there and press R", 55, 155, self.font_small)
        else:
            # Otherwise show current track information
            status = "Playing" if self.is_playing else "Stopped"
            position = self.get_position_seconds()

            self.draw_text(f"Track: {self.get_track_name()}", 55, 120, self.font_text)
            self.draw_text(f"Status: {status}", 55, 160, self.font_text)
            self.draw_text(f"Position: {position:05.1f} sec", 55, 200, self.font_text)
            self.draw_text(f"Playlist: {self.current_index + 1}/{len(self.playlist)}", 55, 240, self.font_text)

        # Controls help line
        self.draw_text("P=Play  S=Stop  N=Next  B=Back  R=Reload  Q=Quit", 55, 320, self.font_small)

        # Temporary message (for example after pressing R)
        if message != "":
            self.draw_text(message, 55, 350, self.font_small, (90, 188, 255))
