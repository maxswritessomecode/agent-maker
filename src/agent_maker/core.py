from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
import json
from pathlib import Path
import re
from typing import Any


SAFE_PRIVACY_CLASSES = {"public", "internal_work", "confidential_work"}
BLOCKED_PRIVACY_CLASSES = {"personal_sensitive", "regulated", "secret"}
KNOWN_PRIVACY_CLASSES = SAFE_PRIVACY_CLASSES | BLOCKED_PRIVACY_CLASSES


@dataclass(frozen=True)
class Source:
    source_id: str
    name: str
    category: str
    availability: str
    approved: bool
    read_only: bool
    freshness: str = "static_export"
    privacy_class: str = "internal_work"
    work_relevance: float = 0.5
    identity_clarity: float = 0.5
    structure: float = 0.5
    signal_density: float = 0.5
    noise_risk: float = 0.5
    evidence_quality: dict[str, bool] = field(default_factory=dict)
    notes: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class SourceScore:
    source_id: str
    score: float
    status: str
    reasons: list[str]


@dataclass(frozen=True)
class Activity:
    activity_id: str
    source_id: str
    actor: str
    occurred_at: str
    activity_type: str
    object_type: str
    object_label: str
    summary: str
    workflow_hints: tuple[str, ...] = ()
    privacy_class: str = "internal_work"
    confidence: float = 0.5
    locator: str = ""


def clamp(value: Any, default: float = 0.5) -> float:
    try:
        number = float(value)
    except (TypeError, ValueError):
        return default
    return max(0.0, min(1.0, number))


def parse_bool(value: Any, field_name: str) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, str):
        lowered = value.strip().lower()
        if lowered == "true":
            return True
        if lowered == "false":
            return False
    raise ValueError(f"{field_name} must be a boolean")


def parse_privacy_class(value: Any) -> str:
    privacy_class = str(value or "internal_work").strip().lower()
    if privacy_class not in KNOWN_PRIVACY_CLASSES:
        raise ValueError(f"unknown privacy_class: {privacy_class}")
    return privacy_class


def parse_workflow_hints(value: Any) -> tuple[str, ...]:
    if value is None:
        return ()
    if isinstance(value, str):
        raw_hints = re.split(r"[,;|]+", value)
    elif isinstance(value, (list, tuple, set)):
        raw_hints = []
        for item in value:
            raw_hints.extend(re.split(r"[,;|]+", str(item)))
    else:
        raise ValueError("workflow_hints must be a string or list of strings")
    hints = []
    for hint in raw_hints:
        normalized = re.sub(r"[^a-z0-9]+", "-", str(hint).lower()).strip("-")
        if normalized:
            hints.append(normalized)
    return tuple(hints)


def slugify(text: str) -> str:
    chars: list[str] = []
    previous_dash = False
    for char in text.lower():
        if char.isalnum():
            chars.append(char)
            previous_dash = False
        elif not previous_dash:
            chars.append("-")
            previous_dash = True
    return "".join(chars).strip("-") or "agent"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def source_from_dict(data: dict[str, Any]) -> Source:
    return Source(
        source_id=str(data["source_id"]),
        name=str(data.get("name") or data["source_id"]),
        category=str(data.get("category") or "unknown"),
        availability=str(data.get("availability") or "local_path"),
        approved=parse_bool(data.get("approved", False), "approved"),
        read_only=parse_bool(data.get("read_only", False), "read_only"),
        freshness=str(data.get("freshness") or "static_export"),
        privacy_class=parse_privacy_class(data.get("privacy_class")),
        work_relevance=clamp(data.get("work_relevance")),
        identity_clarity=clamp(data.get("identity_clarity")),
        structure=clamp(data.get("structure")),
        signal_density=clamp(data.get("signal_density")),
        noise_risk=clamp(data.get("noise_risk")),
        evidence_quality=dict(data.get("evidence_quality") or {}),
        notes=[str(note) for note in data.get("notes", [])],
    )


def activity_from_dict(data: dict[str, Any]) -> Activity:
    hints = data.get("workflow_hints") or data.get("tags") or []
    return Activity(
        activity_id=str(data.get("activity_id") or data.get("id") or ""),
        source_id=str(data["source_id"]),
        actor=str(data.get("actor") or "user"),
        occurred_at=str(data.get("occurred_at") or ""),
        activity_type=str(data.get("activity_type") or "worked"),
        object_type=str(data.get("object_type") or "artifact"),
        object_label=str(data.get("object_label") or "work item"),
        summary=str(data.get("summary") or ""),
        workflow_hints=parse_workflow_hints(hints),
        privacy_class=parse_privacy_class(data.get("privacy_class")),
        confidence=clamp(data.get("confidence")),
        locator=str(data.get("locator") or ""),
    )


def load_manifest(path: Path) -> list[Source]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, dict):
        if "sources" not in payload:
            raise ValueError("manifest must contain a sources list")
        records = payload["sources"]
    else:
        raise ValueError("manifest must be a list or an object with a sources list")
    if not isinstance(records, list):
        raise ValueError("manifest must contain a sources list")
    sources: list[Source] = []
    seen_source_ids: set[str] = set()
    for index, record in enumerate(records, start=1):
        if not isinstance(record, dict):
            raise ValueError(f"invalid manifest source at index {index}: expected object")
        try:
            source = source_from_dict(record)
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"invalid manifest source at index {index}: {exc}") from exc
        if source.source_id in seen_source_ids:
            raise ValueError(f"invalid manifest source at index {index}: duplicate source_id: {source.source_id}")
        seen_source_ids.add(source.source_id)
        sources.append(source)
    return sources


def load_activities(path: Path | None) -> list[Activity]:
    if path is None:
        return []
    activities: list[Activity] = []
    with path.open("r", encoding="utf-8") as activity_file:
        for line_number, line in enumerate(activity_file, start=1):
            stripped = line.strip()
            if not stripped:
                continue
            try:
                decoded = json.loads(stripped)
            except json.JSONDecodeError as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
            if not isinstance(decoded, dict):
                raise ValueError(f"invalid JSONL at line {line_number}: expected object")
            try:
                activities.append(activity_from_dict(decoded))
            except (KeyError, TypeError, ValueError) as exc:
                raise ValueError(f"invalid JSONL at line {line_number}: {exc}") from exc
    return activities


def score_source(source: Source) -> SourceScore:
    reasons: list[str] = []
    if not source.approved:
        return SourceScore(source.source_id, 0.0, "excluded", ["source is not user or enterprise approved"])
    if not source.read_only:
        return SourceScore(source.source_id, 0.0, "excluded", ["source is not read-only"])
    if source.privacy_class in BLOCKED_PRIVACY_CLASSES:
        return SourceScore(source.source_id, 0.0, "excluded", [f"privacy class {source.privacy_class} is blocked"])

    evidence_boost = 0.0
    for key in ("has_stable_ids", "has_timestamps", "has_authors", "has_links"):
        if source.evidence_quality.get(key):
            evidence_boost += 0.05

    score = (
        source.work_relevance * 0.28
        + source.identity_clarity * 0.18
        + source.structure * 0.18
        + source.signal_density * 0.24
        + (1.0 - source.noise_risk) * 0.12
        + evidence_boost
    )
    score = round(min(score, 1.0), 3)

    if score >= 0.8:
        status = "primary"
    elif score >= 0.6:
        status = "supporting"
    elif score >= 0.4:
        status = "limited"
    else:
        status = "low_signal"

    if source.work_relevance >= 0.7:
        reasons.append("high work relevance")
    if source.signal_density >= 0.7:
        reasons.append("contains tasks, decisions, commitments, or status signals")
    if source.noise_risk >= 0.7:
        reasons.append("high noise risk; use with filters")
    if source.privacy_class == "confidential_work":
        reasons.append("confidential source; metadata-first handling recommended")
    if not reasons:
        reasons.append("usable but not a strong standalone source")

    return SourceScore(source.source_id, score, status, reasons)
