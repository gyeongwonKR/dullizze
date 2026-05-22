"""⑥ 영상 합성: props.json 작성 + 품질 게이트 + Remotion render → final.mp4."""
from __future__ import annotations

import json
import math
import subprocess
from pathlib import Path

from pipeline import config

KNOWN_TEMPLATES = ("documentary", "pop")


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


def _quality_gate(template: str, captions: list[dict], assets: list[Path], total: int) -> None:
    """렌더 전 검증 — 깨진 영상 방지(PRD §6 품질 게이트)."""
    if template not in KNOWN_TEMPLATES:
        raise ValueError(f"알 수 없는 템플릿: {template!r} (사용 가능: {KNOWN_TEMPLATES})")
    if not assets:
        raise ValueError("이미지가 없습니다.")
    for a in assets:
        if not a.exists() or a.stat().st_size == 0:
            raise ValueError(f"이미지 파일 누락/빈 파일: {a}")
    if not captions:
        raise ValueError("자막이 없습니다.")
    if any(not c.get("text", "").strip() for c in captions):
        raise ValueError("빈 자막이 포함되어 있습니다.")
    if total <= 0:
        raise ValueError(f"영상 길이가 올바르지 않습니다: {total} frames")


def _build_props(
    mp3: Path, captions: list[dict], assets: list[Path], out_dir: Path, template: str, title: str
) -> Path:
    seconds = _audio_seconds(mp3)
    total = math.ceil(seconds * config.FPS) + config.FPS // 2  # 0.5s 여유

    _quality_gate(template, captions, assets, total)

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
        "template": template,
        "title": title,
    }
    props_path = out_dir / "props.json"
    props_path.write_text(json.dumps(props, ensure_ascii=False), encoding="utf-8")
    return props_path


def render(
    mp3: Path,
    captions: list[dict],
    assets: list[Path],
    out_dir: Path,
    template: str | None = None,
    title: str = "",
) -> Path:
    """final.mp4 생성. 이미 있으면 재사용(멱등)."""
    final = out_dir / "final.mp4"
    if final.exists() and final.stat().st_size > 0:
        return final

    template = template or config.TEMPLATE
    props_path = _build_props(mp3, captions, assets, out_dir, template, title)
    cmd = [
        "npx", "remotion", "render",
        "remotion/src/index.ts", "Main",
        str(final),
        f"--props={props_path}",
        f"--public-dir={out_dir}",
    ]
    subprocess.run(cmd, cwd=config.ROOT, check=True)
    return final
