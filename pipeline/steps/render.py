"""⑥ 영상 합성: props.json 작성 + Remotion render → final.mp4."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from pipeline import config


def _audio_seconds(mp3: Path) -> float:
    out = subprocess.check_output(
        [
            "ffprobe", "-v", "error",
            "-show_entries", "format=duration",
            "-of", "default=nw=1:nk=1",
            str(mp3),
        ]
    )
    return float(out.strip())


def _build_props(mp3: Path, captions: list[dict], assets: list[Path], out_dir: Path) -> Path:
    seconds = _audio_seconds(mp3)
    total = math.ceil(seconds * config.FPS) + config.FPS // 2  # 0.5s 여유

    n = len(assets)
    per = total // n if n else total
    images = []
    for i in range(n):
        start = i * per
        dur = per if i < n - 1 else total - start
        images.append(
            {"src": f"assets/{i:03d}.jpg", "startInFrames": start, "durationInFrames": dur}
        )

    props = {
        "fps": config.FPS,
        "width": config.VIDEO_WIDTH,
        "height": config.VIDEO_HEIGHT,
        "durationInFrames": total,
        "audioSrc": "voice.mp3",
        "images": images,
        "captions": captions,
    }
    props_path = out_dir / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    return props_path


def render(mp3: Path, captions: list[dict], assets: list[Path], out_dir: Path) -> Path:
    """final.mp4 생성. 이미 있으면 재사용(멱등)."""
    final = out_dir / "final.mp4"
    if final.exists() and final.stat().st_size > 0:
        return final

    props_path = _build_props(mp3, captions, assets, out_dir)
    cmd = [
        "npx", "remotion", "render",
        "remotion/src/index.ts", "Main",
        str(final),
        f"--props={props_path}",
        f"--public-dir={out_dir}",
    ]
    subprocess.run(cmd, cwd=config.ROOT, check=True)
    return final
