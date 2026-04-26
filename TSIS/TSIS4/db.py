from __future__ import annotations

try:
    from .main import LeaderboardEntry, LeaderboardStore
except ImportError:  # pragma: no cover - script fallback
    from main import LeaderboardEntry, LeaderboardStore
