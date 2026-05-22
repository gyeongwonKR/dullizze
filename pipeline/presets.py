"""파일 기반 프리셋(생성 설정 묶음) 유틸리티.

프리셋 = 사용자가 저장한 '스타일 레시피'(주제 제외). job = 프리셋 + 주제.
저장: data/presets/<user_id>.json → { preset_id: {preset...} }
"""
from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from pipeline import accounts
from pipeline import config

# 프리셋이 담는 필드(주제 제외). 파이프라인을 실제로 통과하는 것만.
# 뒤 4개(channel_name~accent_color)는 banner 템플릿의 채널 브랜딩/강조색.
PRESET_FIELDS = (
    "template", "tone", "visual_mode", "visual_provider", "voice", "model",
    "channel_name", "footer_main", "footer_accent", "accent_color",
)


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _path(user_id: str) -> Path:
    return config.PRESETS_DIR / f"{user_id}.json"


def _load_all(user_id: str) -> dict[str, dict[str, Any]]:
    p = _path(user_id)
    if not p.exists():
        return {}
    return json.loads(p.read_text(encoding="utf-8"))


def _save_all(user_id: str, data: dict[str, dict[str, Any]]) -> None:
    config.PRESETS_DIR.mkdir(parents=True, exist_ok=True)
    _path(user_id).write_text(
        json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8"
    )


def _normalize_fields(fields: dict[str, Any]) -> dict[str, Any]:
    """프리셋 필드를 검증·정규화."""
    return {
        "template": config.validate_template(fields.get("template")),
        "tone": (fields.get("tone") or config.DEFAULT_TONE).strip(),
        "visual_mode": config.validate_visual_mode(fields.get("visual_mode")),
        "visual_provider": config.validate_visual_provider(fields.get("visual_provider")),
        "voice": config.normalize_voice(fields.get("voice")),
        "model": config.normalize_model(fields.get("model")),
        "channel_name": (fields.get("channel_name") or "").strip(),
        "footer_main": (fields.get("footer_main") or "").strip(),
        "footer_accent": (fields.get("footer_accent") or "").strip(),
        "accent_color": config.normalize_accent_color(fields.get("accent_color")),
    }


def list_presets(user_id: str | None = None) -> list[dict[str, Any]]:
    user_id = accounts.normalize_user_id(user_id)
    return list(_load_all(user_id).values())


def get_preset(user_id: str | None, preset_id: str) -> dict[str, Any]:
    user_id = accounts.normalize_user_id(user_id)
    preset_id = config.validate_preset_id(preset_id)
    data = _load_all(user_id)
    if preset_id not in data:
        raise FileNotFoundError(f"프리셋을 찾을 수 없습니다: {preset_id}")
    return data[preset_id]


def save_preset(
    user_id: str | None,
    name: str,
    fields: dict[str, Any],
    preset_id: str | None = None,
) -> dict[str, Any]:
    """프리셋 생성(preset_id 없음) 또는 수정(preset_id 지정)."""
    user_id = accounts.normalize_user_id(user_id)
    name = (name or "").strip()
    if not name:
        raise ValueError("프리셋 이름(name)은 비워둘 수 없습니다.")
    data = _load_all(user_id)
    now = _now_iso()
    if preset_id:
        preset_id = config.validate_preset_id(preset_id)
        created = data.get(preset_id, {}).get("created_at", now)
    else:
        preset_id = config.new_preset_id()
        created = now
    preset = {
        "preset_id": preset_id,
        "user_id": user_id,
        "name": name,
        **_normalize_fields(fields),
        "created_at": created,
        "updated_at": now,
    }
    data[preset_id] = preset
    _save_all(user_id, data)
    return preset


def delete_preset(user_id: str | None, preset_id: str) -> None:
    user_id = accounts.normalize_user_id(user_id)
    preset_id = config.validate_preset_id(preset_id)
    data = _load_all(user_id)
    if preset_id not in data:
        raise FileNotFoundError(f"프리셋을 찾을 수 없습니다: {preset_id}")
    del data[preset_id]
    _save_all(user_id, data)


def resolve(user_id: str | None, preset_id: str | None) -> dict[str, Any]:
    """프리셋 필드를 dict로 반환. preset_id 없음/'auto' → {} (시스템 기본값 사용)."""
    if not preset_id or preset_id.strip().lower() == "auto":
        return {}
    preset = get_preset(user_id, preset_id)
    return {k: preset[k] for k in PRESET_FIELDS if k in preset}
