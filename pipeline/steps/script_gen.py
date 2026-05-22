"""① 스크립트 생성: Claude API → script.json."""
from __future__ import annotations

import json
import re
from pathlib import Path

from anthropic import Anthropic

from pipeline import config

SYSTEM = """너는 한국어 정보/지식형 YouTube 쇼츠 작가다.
주어진 주제로 9:16 쇼츠 1편의 나레이션과 비주얼 계획을 만든다.

규칙:
- 나레이션은 자연스러운 구어체 한국어. 소리 내어 읽으면 38~48초 분량. 한국어 280~360자, 6~8개의 짧은 문장. 절대 380자를 넘기지 말 것(길이 초과는 실패).
- 강한 훅으로 시작(첫 문장에서 호기심 유발), 흥미로운 사실 위주 본문, 짧은 마무리(CTA).
- 팩트는 정확하게. 추측이면 단정하지 말 것.
- visual_prompts는 영어로, 각 장면을 묘사하는 이미지 생성 프롬프트. 세로 9:16, 시네마틱.

반드시 아래 JSON만 출력(코드블록/설명 금지):
{
  "narration": "전체 나레이션 (훅+본문+마무리를 하나로 합친, TTS가 읽을 텍스트)",
  "hook": "첫 훅 문장",
  "cta": "마무리 문장",
  "visual_prompts": ["english prompt 1", "... 총 %d개"],
  "title": "유튜브 제목 (40자 이내)",
  "tags": ["태그", "..."],
  "description": "유튜브 설명 (2~3문장)"
}"""


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


def generate(topic: str, out_dir: Path, tone: str | None = None) -> dict:
    """주제 → script.json. 이미 있으면 재사용(멱등)."""
    out = out_dir / "script.json"
    if out.exists():
        return json.loads(out.read_text(encoding="utf-8"))

    if not config.ANTHROPIC_API_KEY:
        raise RuntimeError("ANTHROPIC_API_KEY가 .env에 설정되지 않았습니다.")

    tone = tone or config.DEFAULT_TONE
    client = Anthropic(api_key=config.ANTHROPIC_API_KEY)
    msg = client.messages.create(
        model=config.CLAUDE_MODEL,
        max_tokens=2000,
        system=SYSTEM % config.NUM_VISUALS,
        messages=[
            {
                "role": "user",
                "content": f"주제: {topic}\n톤: {tone}\n비주얼 개수: {config.NUM_VISUALS}",
            }
        ],
    )
    data = _extract_json(msg.content[0].text)
    data["topic"] = topic
    out.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data
