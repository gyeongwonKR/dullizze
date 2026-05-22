"""⑤ 자막 타이밍: faster-whisper → captions.json (word-level)."""
from __future__ import annotations

import json
from pathlib import Path

from faster_whisper import WhisperModel

from pipeline import config


def transcribe(mp3: Path, out_dir: Path) -> list[dict]:
    """voice.mp3 → 단어별 타임스탬프. 이미 있으면 재사용(멱등).

    표시 텍스트로 whisper가 인식한 단어를 그대로 사용하므로,
    각 단어가 실제 발화 구간에 표시되어 음성과 동기화된다.
    """
    out = out_dir / "captions.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))

    model = WhisperModel(config.WHISPER_MODEL, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(str(mp3), language="ko", word_timestamps=True)

    words: list[dict] = []
    for seg in segments:
        for w in seg.words or []:
            text = w.word.strip()
            if not text:
                continue
            words.append(
                {
                    "text": text,
                    "startMs": int(w.start * 1000),
                    "endMs": int(w.end * 1000),
                }
            )

    out.write_text(json.dumps(words, ensure_ascii=False, indent=2), encoding="utf-8")
    return words
