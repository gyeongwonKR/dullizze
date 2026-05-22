"""③ TTS: edge-tts → voice.mp3 (지수 백오프 재시도)."""
from __future__ import annotations

import asyncio
from pathlib import Path

import edge_tts

from pipeline import config


async def _synthesize(text: str, voice: str, out: Path, retries: int = 3) -> None:
    delay = 2.0
    for attempt in range(1, retries + 1):
        try:
            communicate = edge_tts.Communicate(text, voice)
            await communicate.save(str(out))
            if out.stat().st_size > 0:
                return
            raise RuntimeError("빈 mp3 생성됨")
        except Exception as e:  # noqa: BLE001 - 단계별로 잡아 재시도
            if attempt == retries:
                raise
            print(f"  [tts] 시도 {attempt} 실패({e!r}), {delay:.0f}s 후 재시도")
            await asyncio.sleep(delay)
            delay *= 2


def synthesize(text: str, out_dir: Path, voice: str | None = None) -> Path:
    """나레이션 텍스트 → voice.mp3. 이미 있으면 재사용(멱등)."""
    out = out_dir / "voice.mp3"
    if out.exists() and out.stat().st_size > 0:
        return out
    voice = voice or config.DEFAULT_VOICE
    asyncio.run(_synthesize(text, voice, out))
    return out
