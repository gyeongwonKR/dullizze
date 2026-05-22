"""파일 기반 사용자/쿼터 유틸리티."""
from __future__ import annotations

import json
from datetime import date
from typing import Any

from pipeline import config

COUNTED_STATUSES = {"queued", "running", "done"}


def normalize_user_id(user_id: str | None = None) -> str:
    user_id = (user_id or config.DEFAULT_USER_ID).strip()
    return config.validate_user_id(user_id)


def normalize_plan(plan: str | None = None) -> str:
    plan = (plan or config.DEFAULT_PLAN).strip().lower()
    if plan not in config.PLAN_MONTHLY_QUOTAS:
        raise ValueError(f"알 수 없는 plan입니다: {plan}")
    return plan


def month_key(d: date | None = None) -> str:
    d = d or date.today()
    return d.strftime("%Y-%m")


def _iter_month_jobs(month: str) -> list[dict[str, Any]]:
    root = config.ROOT / "runs"
    jobs: list[dict[str, Any]] = []
    for path in root.glob(f"{month}-*/*/job.json"):
        try:
            jobs.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception:
            continue
    return jobs


def usage_count(user_id: str, month: str | None = None, exclude_job_id: str | None = None) -> int:
    user_id = normalize_user_id(user_id)
    month = month or month_key()
    count = 0
    for job in _iter_month_jobs(month):
        if job.get("job_id") == exclude_job_id:
            continue
        if job.get("user_id", config.DEFAULT_USER_ID) != user_id:
            continue
        if job.get("status") in COUNTED_STATUSES:
            count += 1
    return count


def quota_snapshot(
    user_id: str | None = None,
    plan: str | None = None,
    month: str | None = None,
    exclude_job_id: str | None = None,
) -> dict[str, Any]:
    user_id = normalize_user_id(user_id)
    plan = normalize_plan(plan)
    month = month or month_key()
    limit = config.PLAN_MONTHLY_QUOTAS[plan]
    used = usage_count(user_id, month, exclude_job_id)
    return {
        "user_id": user_id,
        "plan": plan,
        "month": month,
        "limit": limit,
        "used": used,
        "remaining": max(limit - used, 0),
    }


def ensure_quota_available(job: dict[str, Any]) -> dict[str, Any]:
    quota = quota_snapshot(
        user_id=job.get("user_id"),
        plan=job.get("plan"),
        exclude_job_id=job.get("job_id"),
    )
    if quota["remaining"] <= 0:
        raise PermissionError(
            f"월 생성 쿼터를 초과했습니다: {quota['used']}/{quota['limit']} ({quota['plan']})"
        )
    return quota
