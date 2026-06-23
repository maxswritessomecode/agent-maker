from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
import re
from typing import Iterable

from .core import Activity, BLOCKED_PRIVACY_CLASSES, Source, SourceScore, score_source, slugify


BLOCKED_WORKFLOW_HINTS = {
    "hr",
    "hiring",
    "performance",
    "performance-review",
    "legal",
    "medical",
    "financial-advice",
    "customer-eligibility",
    "employee-monitoring",
}

RAW_BLOCKED_TEXT_TERMS = {
    "background check",
    "candidate evaluation",
    "compensation review",
    "customer eligibility",
    "employee monitoring",
    "financial advice",
    "health diagnosis",
    "hiring decision",
    "legal advice",
    "medical advice",
    "performance calibration",
    "performance review",
    "promotion decision",
    "regulated data",
    "termination decision",
}
BLOCKED_TEXT_TERMS = {re.sub(r"[^a-z0-9]+", " ", term).strip() for term in RAW_BLOCKED_TEXT_TERMS}

ROLE_TEMPLATES = {
    "meeting": {
        "name": "Meeting Follow-up Coordinator",
        "mission": "Turn approved meeting context into follow-up drafts, open-loop lists, and weekly meeting summaries.",
        "actions": ["summarize approved meeting notes", "extract likely action items", "draft follow-up messages", "maintain open-loop reports"],
    },
    "email": {
        "name": "Inbox Triage Partner",
        "mission": "Help prioritize routine work email, draft responses, and surface unresolved commitments.",
        "actions": ["classify approved email threads", "draft replies for review", "summarize unresolved threads", "prepare daily inbox briefs"],
    },
    "status": {
        "name": "Status Update Assistant",
        "mission": "Collect approved work signals and draft status updates, stakeholder summaries, and weekly reports.",
        "actions": ["draft status updates", "summarize progress signals", "highlight blockers", "prepare stakeholder-ready reports"],
    },
    "project": {
        "name": "Project Open-Loops Tracker",
        "mission": "Track repeated project commitments and prepare reviewable open-loop reports.",
        "actions": ["extract project commitments", "group open loops by project", "draft reminders for review", "prepare weekly follow-up lists"],
    },
    "decision": {
        "name": "Decision Memo Partner",
        "mission": "Synthesize approved discussions and documents into decision-prep memos with caveats and evidence.",
        "actions": ["summarize decision context", "compare options", "draft decision memos", "list assumptions and unresolved questions"],
    },
    "default": {
        "name": "Work Pattern Assistant",
        "mission": "Help with recurring knowledge-work patterns found in approved work context.",
        "actions": ["summarize approved context", "draft reusable work artifacts", "track repeated requests", "prepare review notes"],
    },
}


@dataclass(frozen=True)
class Proposal:
    agent_slug: str
    agent_name: str
    mission: str
    pattern: str
    confidence: float
    opportunity_score: int
    scorecard: tuple[str, ...]
    risk_level: str
    evidence_count: int
    source_ids: tuple[str, ...]
    evidence_notes: tuple[str, ...]
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    required_confirmations: tuple[str, ...]
    output_dirs: tuple[str, ...]
    success_metrics: tuple[str, ...]


def source_scores_by_id(sources: Iterable[Source]) -> dict[str, SourceScore]:
    return {source.source_id: score_source(source) for source in sources}


def approved_source_ids(sources: Iterable[Source]) -> set[str]:
    scores = source_scores_by_id(sources)
    return {source_id for source_id, score in scores.items() if score.status in {"primary", "supporting", "limited"}}


def classify_pattern(activity: Activity) -> str:
    hints = set(activity.workflow_hints)
    blocked = hints & BLOCKED_WORKFLOW_HINTS
    if blocked:
        return "blocked"
    text = normalize_match_text(" ".join([activity.activity_type, activity.object_type, activity.object_label, activity.summary, *activity.workflow_hints]))
    if any(term in text for term in BLOCKED_TEXT_TERMS):
        return "blocked"
    if {"meeting", "calendar", "transcript", "minutes"} & hints or "meeting" in text:
        return "meeting"
    if {"email", "inbox"} & hints or activity.object_type == "email":
        return "email"
    if {"status", "report", "weekly-update"} & hints or "status" in text:
        return "status"
    if {"project", "task", "ticket", "open-loop"} & hints or activity.object_type in {"ticket", "task"}:
        return "project"
    if {"decision", "memo", "strategy"} & hints or "decision" in text:
        return "decision"
    return "default"


def normalize_match_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def generate_proposals(sources: list[Source], activities: list[Activity], limit: int = 3) -> list[Proposal]:
    limit = max(0, min(3, limit))
    allowed_sources = approved_source_ids(sources)
    usable = [
        activity
        for activity in activities
        if (
            activity.source_id in allowed_sources
            and activity.privacy_class not in BLOCKED_PRIVACY_CLASSES
            and classify_pattern(activity) != "blocked"
        )
    ]
    if not usable:
        return []

    grouped: dict[str, list[Activity]] = defaultdict(list)
    for activity in usable:
        grouped[classify_pattern(activity)].append(activity)

    ranked_patterns = sorted(
        grouped.items(),
        key=lambda item: (len(item[1]), sum(activity.confidence for activity in item[1])),
        reverse=True,
    )

    proposals: list[Proposal] = []
    for pattern, pattern_activities in ranked_patterns[:limit]:
        template = ROLE_TEMPLATES.get(pattern, ROLE_TEMPLATES["default"])
        source_counts = Counter(activity.source_id for activity in pattern_activities)
        evidence_notes = tuple(
            _evidence_note(activity) for activity in pattern_activities[:5]
        )
        avg_confidence = sum(activity.confidence for activity in pattern_activities) / len(pattern_activities)
        agent_name = template["name"]
        slug = slugify(agent_name)
        source_scores = [score_source(source) for source in sources if source.source_id in source_counts]
        source_quality = _source_quality(source_scores)
        repeatability = _repeatability(pattern_activities)
        frequency = _frequency_score(pattern_activities)
        risk_level = _risk_level(pattern, source_scores)
        opportunity_score = _opportunity_score(frequency, repeatability, source_quality, risk_level)
        proposals.append(
            Proposal(
                agent_slug=slug,
                agent_name=agent_name,
                mission=template["mission"],
                pattern=pattern,
                confidence=_confidence(avg_confidence, len(pattern_activities), source_quality),
                opportunity_score=opportunity_score,
                scorecard=(
                    f"Frequency: {frequency}/5 based on {len(pattern_activities)} evidence records in the lookback window.",
                    f"Repeatability: {repeatability}/5 based on recurring work artifacts and workflow hints.",
                    f"Source quality: {source_quality}/5 based on approved, read-only source scores.",
                    f"Risk: {risk_level}; recommended first version stays draft-only and human-reviewed.",
                    f"Expected first useful output: {template['actions'][0]}.",
                ),
                risk_level=risk_level,
                evidence_count=len(pattern_activities),
                source_ids=tuple(source_id for source_id, _ in source_counts.most_common()),
                evidence_notes=evidence_notes,
                allowed_actions=tuple(template["actions"]),
                blocked_actions=(
                    "send messages or emails without human approval",
                    "modify source systems",
                    "evaluate employee performance",
                    "make legal, medical, financial, HR, hiring, or eligibility decisions",
                    "use unapproved sources",
                ),
                required_confirmations=(
                    "Confirm this role matches a real pain point.",
                    "Confirm the listed sources are approved for this agent.",
                    "Confirm output folders and retention expectations.",
                    "Confirm whether the agent may draft, summarize, classify, or only advise.",
                ),
                output_dirs=(
                    f"Agent Work/{slug}/config",
                    f"Agent Work/{slug}/drafts",
                    f"Agent Work/{slug}/reports",
                    f"Agent Work/{slug}/archive",
                ),
                success_metrics=(
                    "User keeps or refines the proposal after review.",
                    "Draft outputs require less editing over time.",
                    "The agent reduces repeated manual preparation work.",
                ),
            )
        )
    return proposals


def _frequency_score(activities: list[Activity]) -> int:
    count = len(activities)
    if count >= 8:
        return 5
    if count >= 5:
        return 4
    if count >= 3:
        return 3
    if count >= 2:
        return 2
    return 1


def _repeatability(activities: list[Activity]) -> int:
    labels = {normalize_match_text(activity.object_label) for activity in activities if activity.object_label}
    hints = {hint for activity in activities for hint in activity.workflow_hints}
    score = 1
    if len(activities) >= 2:
        score += 1
    if len(labels) < len(activities):
        score += 1
    if {"weekly-update", "open-loop", "status", "follow-up", "meeting", "email"} & hints:
        score += 1
    if len(hints) >= 3:
        score += 1
    return min(score, 5)


def _source_quality(scores: list[SourceScore]) -> int:
    if not scores:
        return 1
    average = sum(score.score for score in scores) / len(scores)
    if average >= 0.85:
        return 5
    if average >= 0.72:
        return 4
    if average >= 0.6:
        return 3
    if average >= 0.45:
        return 2
    return 1


def _risk_level(pattern: str, scores: list[SourceScore]) -> str:
    if any(score.status == "limited" for score in scores):
        return "medium"
    if pattern in {"email", "decision"}:
        return "medium"
    return "low"


def _opportunity_score(frequency: int, repeatability: int, source_quality: int, risk_level: str) -> int:
    risk_penalty = {"low": 0, "medium": 1, "high": 2}.get(risk_level, 1)
    raw = (frequency * 0.32 + repeatability * 0.32 + source_quality * 0.36) - risk_penalty
    return max(1, min(5, round(raw)))


def _confidence(avg_confidence: float, evidence_count: int, source_quality: int) -> float:
    evidence_cap = 0.62
    if evidence_count >= 8:
        evidence_cap = 0.92
    elif evidence_count >= 5:
        evidence_cap = 0.86
    elif evidence_count >= 3:
        evidence_cap = 0.78
    elif evidence_count >= 2:
        evidence_cap = 0.70
    quality_adjustment = (source_quality - 3) * 0.02
    return round(max(0.1, min(evidence_cap, avg_confidence + quality_adjustment)), 2)


def _evidence_note(activity: Activity) -> str:
    locator = f" ({activity.locator})" if activity.locator else ""
    label = activity.object_label.replace("\n", " ").strip()
    summary = activity.summary.replace("\n", " ").strip()
    if len(summary) > 180:
        summary = summary[:177].rstrip() + "..."
    return f"{activity.occurred_at}: {activity.activity_type} {activity.object_type} '{label}' - {summary}{locator}"
