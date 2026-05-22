"""중앙 설정: .env 로드 + 경로/상수."""
from __future__ import annotations

import os
from datetime import date
from pathlib import Path

from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")

# --- 영상 사양 (9:16 쇼츠) ---
VIDEO_WIDTH = 1080
VIDEO_HEIGHT = 1920
FPS = 30

# --- API / 모델 ---
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = os.getenv("CLAUDE_MODEL", "claude-sonnet-4-6")

# --- TTS ---
DEFAULT_VOICE = os.getenv("DEFAULT_VOICE", "ko-KR-SunHiNeural")
DEFAULT_TONE = os.getenv("DEFAULT_TONE", "흥미로운_사실")

# --- 자막 (faster-whisper) ---
# PRD는 large-v3 권장(프로덕션 품질). CPU 반복 테스트 속도를 위해 기본은 small,
# .env의 WHISPER_MODEL로 large-v3 등으로 교체 가능.
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")

# --- 비주얼 ---
NUM_VISUALS = int(os.getenv("NUM_VISUALS", "5"))


def run_dir(d: date | None = None) -> Path:
    """runs/YYYY-MM-DD/ 경로 반환 (없으면 생성)."""
    d = d or date.today()
    p = ROOT / "runs" / d.isoformat()
    (p / "assets").mkdir(parents=True, exist_ok=True)
    (p / "logs").mkdir(parents=True, exist_ok=True)
    return p
