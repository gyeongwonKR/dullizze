"""④ 비주얼 수집: Pollinations.ai → assets/*.jpg (키 불필요, asyncio)."""
from __future__ import annotations

import asyncio
from pathlib import Path
from urllib.parse import quote

import aiohttp

from pipeline import config

BASE = "https://image.pollinations.ai/prompt/"


async def _fetch(session: aiohttp.ClientSession, prompt: str, out: Path, seed: int, retries: int = 3) -> Path:
    if out.exists() and out.stat().st_size > 0:
        return out
    url = (
        BASE
        + quote(prompt)
        + f"?width={config.VIDEO_WIDTH}&height={config.VIDEO_HEIGHT}&nologo=true&seed={seed}"
    )
    delay = 2.0
    for attempt in range(1, retries + 1):
        try:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=120)) as resp:
                resp.raise_for_status()
                data = await resp.read()
            if len(data) < 1000:
                raise RuntimeError(f"이미지가 너무 작음({len(data)}B)")
            out.write_bytes(data)
            return out
        except Exception as e:  # noqa: BLE001 - 단계별로 잡아 재시도
            if attempt == retries:
                raise
            print(f"  [visuals] {out.name} 시도 {attempt} 실패({e!r}), {delay:.0f}s 후 재시도")
            await asyncio.sleep(delay)
            delay *= 2
    return out


async def _gather(prompts: list[str], assets_dir: Path) -> list[Path]:
    # Pollinations 익명 티어는 동시 요청을 402(rate limit)로 막으므로 순차 처리.
    results: list[Path] = []
    async with aiohttp.ClientSession() as session:
        for i, p in enumerate(prompts):
            out = assets_dir / f"{i:03d}.jpg"
            cached = out.exists() and out.stat().st_size > 0
            if i > 0 and not cached:
                await asyncio.sleep(1.0)  # 익명 티어 rate limit 회피
            results.append(await _fetch(session, p, out, seed=i))
    return results


def collect(prompts: list[str], out_dir: Path) -> list[Path]:
    """비주얼 프롬프트 목록 → assets/*.jpg. 이미 있으면 재사용(멱등)."""
    assets_dir = out_dir / "assets"
    assets_dir.mkdir(parents=True, exist_ok=True)
    return asyncio.run(_gather(prompts, assets_dir))
