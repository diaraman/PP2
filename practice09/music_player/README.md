# Music Player (Keyboard Controller)

## Controls
- `P` = Play current track
- `S` = Stop
- `N` = Next track
- `B` = Previous track
- `R` = Reload playlist (rescans `music/`)
- `Q` = Quit

## Features
- Playlist management from `music/` folder
- Displays current track name
- Displays playback status and current position in seconds
- Auto-plays next track when current one ends

## Structure
```
Practice7/
└── music_player/
    ├── main.py
    ├── player.py
    ├── music/
    │   ├── track1.wav
    │   └── track2.wav
    └── README.md
```

## Run
```bash
cd Practice7/music_player
python3 main.py
```

If `pygame` is not installed, install it for your Python first.
