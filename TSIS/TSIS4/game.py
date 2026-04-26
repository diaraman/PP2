from __future__ import annotations

try:
    from .main import Obstacle, PowerUp, Settings, SnakeGame
except ImportError:  # pragma: no cover - script fallback
    from main import Obstacle, PowerUp, Settings, SnakeGame
