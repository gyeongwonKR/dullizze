"""① 스크립트 생성: Claude API → script.json."""
from __future__ import annotations

import json
import logging
import re
from pathlib import Path
from typing import Any

from anthropic import Anthropic

from pipeline import config

SYSTEM = """너는 한국어 정보/지식형 YouTube 쇼츠 작가다.
주어진 주제로 9:16 쇼츠 1편의 나레이션과 비주얼 계획을 만든다.

규칙:
- 나레이션은 자연스러운 구어체 한국어. 소리 내어 읽으면 38~48초 분량. 한국어 280~360자, 6~8개의 짧은 문장. 절대 380자를 넘기지 말 것(길이 초과는 실패).
- 강한 훅으로 시작(첫 문장에서 호기심 유발), 흥미로운 사실 위주 본문, 짧은 마무리(CTA).
- 팩트는 정확하게. 추측이면 단정하지 말 것.
- visual_prompts는 영어로, 각 장면을 묘사하는 이미지 생성 프롬프트. 세로 9:16, 시네마틱.
- headline_main/headline_accent는 영상 상단에 띄울 2줄짜리 온스크린 헤드라인이다(유튜브 제목과 별개). 각 줄 한국어 12자 이내로 짧고 강하게. main은 도입, accent는 결정타.

반드시 아래 JSON만 출력(코드블록/설명 금지):
{
  "narration": "전체 나레이션 (훅+본문+마무리를 하나로 합친, TTS가 읽을 텍스트)",
  "hook": "첫 훅 문장",
  "cta": "마무리 문장",
  "visual_prompts": ["english prompt 1", "... 총 %d개"],
  "headline_main": "온스크린 헤드라인 1줄 (≤12자)",
  "headline_accent": "온스크린 헤드라인 2줄, 강조색 (≤12자)",
  "title": "유튜브 제목 (40자 이내)",
  "tags": ["태그", "..."],
  "description": "유튜브 설명 (2~3문장)"
}"""

HAIKU_4_5_PRICING_USD_PER_MTOK = {
    "input_tokens": 1.00,
    "cache_creation_input_tokens": 1.25,  # 5분 ephemeral cache write
    "cache_read_input_tokens": 0.10,
    "output_tokens": 5.00,
}
HAIKU_4_5_CACHE_MIN_TOKENS = 4096


def _extract_json(text: str) -> dict:
    """모델 출력에서 JSON 객체 추출."""
    text = text.strip()
    # 코드블록이 있으면 제거
    text = re.sub(r"^```(?:json)?\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        raise ValueError(f"JSON을 찾을 수 없음: {text[:200]}")
    return json.loads(text[start : end + 1])


def _system_prompt() -> str | list[dict[str, Any]]:
    """정적 시스템 프롬프트에 Anthropic prompt cache breakpoint를 붙인다."""
    text = SYSTEM % config.NUM_VISUALS
    if not config.CLAUDE_PROMPT_CACHE:
        return text
    return [
        {
            "type": "text",
            "text": text,
            "cache_control": {"type": "ephemeral"},
        }
    ]


def _usage_dict(usage: object | None) -> dict[str, int]:
    fields = (
        "input_tokens",
        "cache_creation_input_tokens",
        "cache_read_input_tokens",
        "output_tokens",
    )
    result: dict[str, int] = {}
    for field in fields:
        value = getattr(usage, field, 0) if usage is not None else 0
        result[field] = int(value or 0)
    result["total_input_tokens"] = (
        result["input_tokens"]
        + result["cache_creation_input_tokens"]
        + result["cache_read_input_tokens"]
    )
    return result


def _estimate_cost_usd(usage: dict[str, int], model: str) -> float | None:
    if not model.startswith("claude-haiku-4-5"):
        return None
    cost = 0.0
    for field, price in HAIKU_4_5_PRICING_USD_PER_MTOK.items():
        cost += usage[field] * price / 1_000_000
    return round(cost, 8)


def _write_usage_log(out_dir: Path, usage: object | None, model: str) -> None:
    usage_data = _usage_dict(usage)
    cache_tokens = usage_data["cache_creation_input_tokens"] + usage_data["cache_read_input_tokens"]
    is_haiku = model.startswith("claude-haiku-4-5")
    payload = {
        "model": model,
        "prompt_cache_enabled": config.CLAUDE_PROMPT_CACHE,
        "prompt_cache_type": "ephemeral" if config.CLAUDE_PROMPT_CACHE else None,
        "prompt_cache_min_tokens": HAIKU_4_5_CACHE_MIN_TOKENS if is_haiku else None,
        "prompt_cache_note": "Haiku 4.5는 4096토큰 이상 프롬프트만 실제 캐시됩니다."
        if is_haiku
        else None,
        "prompt_cache_used": cache_tokens > 0,
        "usage": usage_data,
        "pricing_usd_per_mtok": HAIKU_4_5_PRICING_USD_PER_MTOK if is_haiku else None,
        "estimated_cost_usd": _estimate_cost_usd(usage_data, model),
    }
    log_path = out_dir / "logs" / "script_usage.json"
    log_path.parent.mkdir(parents=True, exist_ok=True)
    log_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    logging.getLogger("pipeline").info(
        "Claude usage: input=%d cache_write=%d cache_read=%d output=%d cost=%s",
        usage_data["input_tokens"],
        usage_data["cache_creation_input_tokens"],
        usage_data["cache_read_input_tokens"],
        usage_data["output_tokens"],
        payload["estimated_cost_usd"],
    )


def generate(topic: str, out_dir: Path, tone: str | None = None, model: str | None = None) -> dict:
    """주제 → script.json. 이미 있으면 재사용(멱등)."""
    out = out_dir / "script.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))

    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.")

    tone = tone or config.DEFAULT_TONE
    model = config.normalize_model(model)
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=model,
        max_tokens=2000,
        system=_system_prompt(),
        messages=[
            {
                "role": "user",
                "content": f"주제: {topic}\n톤: {tone}\n비주얼 개수: {config.NUM_VISUALS}",
            }
        ],
    )
    _write_usage_log(out_dir, msg.usage, model)
    data = _extract_json(msg.content[0].text)
    data["topic"] = topic
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
