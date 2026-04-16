# Practice09 - Pygame Projects

This folder contains 3 beginner-friendly pygame tasks:

## 1) Mickey's Clock (`mickeys_clock/`)
A Mickey-themed clock that uses hand graphics and updates with system time.

### Features
- Shows minutes and seconds
- Rotates Mickey hands in real time
- Uses `pygame.transform.rotate()`

### Run
```bash
python3 mickeys_clock/main.py
```

## 2) Music Player (`music_player/`)
Keyboard-controlled music player with playlist support.

### Controls
- `P` = Play
- `S` = Stop
- `N` = Next track
- `B` = Previous track
- `R` = Reload playlist
- `Q` = Quit

### Features
- Playlist loading from `music_player/music`
- Track name/status/progress display
- Auto-next when track ends

### Run
```bash
python3 music_player/main.py
```

## 3) Moving Ball Game (`moving_ball/`)
Simple white-screen game with a red ball controlled by arrow keys.

### Features
- Ball radius = `25` (size 50x50)
- Arrow key movement
- Step size = `20` pixels
- Ball cannot go outside screen boundaries
- Supports continuous movement while key is held

### Run
```bash
python3 moving_ball/main.py
```

## Requirements
Install dependency:
```bash
python3 -m pip install -r requirements.txt
```

Or directly:
```bash
python3 -m pip install pygame
```
