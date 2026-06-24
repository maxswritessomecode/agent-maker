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
    "candidate ranking",
    "compensation review",
    "customer eligibility",
    "employee monitoring",
    "financial advice",
    "health diagnosis",
    "hiring decision",
    "interview debrief",
    "legal advice",
    "medical advice",
    "new hire onboarding",
    "performance calibration",
    "performance review",
    "promotion decision",
    "regulated data",
    "resume screening",
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
    "sales": {
        "name": "Account Briefing Assistant",
        "mission": "Prepare account, lead, and call briefs from approved CRM, email, meeting, and company research context.",
        "actions": ["draft account briefs", "summarize approved customer context", "prepare call prep notes", "list follow-up questions"],
    },
    "support": {
        "name": "Support Triage Assistant",
        "mission": "Summarize support requests, draft responses, and group customer issues for human review.",
        "actions": ["classify support requests", "draft response options", "summarize escalations", "prepare handoff notes"],
    },
    "content": {
        "name": "Content Repurposing Assistant",
        "mission": "Turn approved source material into draft posts, newsletters, briefs, and content outlines.",
        "actions": ["summarize source material", "draft platform-specific content", "extract reusable points", "prepare editorial review notes"],
    },
    "release": {
        "name": "Release Notes Assistant",
        "mission": "Turn approved issue, PR, changelog, and ticket context into draft release notes and stakeholder summaries.",
        "actions": ["summarize merged work", "draft release notes", "group changes by audience", "highlight risks and follow-ups"],
    },
    "research": {
        "name": "Research Briefing Assistant",
        "mission": "Compile approved research signals into concise briefs with sources, caveats, and next questions.",
        "actions": ["summarize research sources", "compare findings", "draft briefing notes", "list assumptions and evidence gaps"],
    },
    "default": {
        "name": "Work Pattern Assistant",
        "mission": "Help with recurring knowledge-work patterns found in approved work context.",
        "actions": ["summarize approved context", "draft reusable work artifacts", "track repeated requests", "prepare review notes"],
    },
}


@dataclass(frozen=True)
class ScorecardDetail:
    label: str
    score: int
    max_score: int
    summary: str
    details: tuple[str, ...]


@dataclass(frozen=True)
class EvidenceNote:
    text: str
    classified_as: str
    classification_signals: tuple[str, ...]


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
    evidence_notes: tuple[EvidenceNote, ...]
    allowed_actions: tuple[str, ...]
    blocked_actions: tuple[str, ...]
    required_confirmations: tuple[str, ...]
    output_dirs: tuple[str, ...]
    success_metrics: tuple[str, ...]
    scorecard_details: tuple[ScorecardDetail, ...] = ()
    confidence_breakdown: tuple[str, ...] = ()
    dropped_reason: str = ""


@dataclass(frozen=True)
class ProposalBatch:
    selected: tuple[Proposal, ...]
    rejected: tuple[Proposal, ...]


def source_scores_by_id(sources: Iterable[Source]) -> dict[str, SourceScore]:
    return {source.source_id: score_source(source) for source in sources}


def approved_source_ids(sources: Iterable[Source]) -> set[str]:
    scores = source_scores_by_id(sources)
    return {source_id for source_id, score in scores.items() if score.status in {"primary", "supporting", "limited"}}


def classify_pattern(activity: Activity) -> str:
    return classify_activity(activity)[0]


def classify_activity(activity: Activity) -> tuple[str, tuple[str, ...]]:
    hints = set(activity.workflow_hints)
    blocked = hints & BLOCKED_WORKFLOW_HINTS
    if blocked:
        return "blocked", tuple(f'workflow_hint="{hint}"' for hint in sorted(blocked))
    text = normalize_match_text(" ".join([activity.activity_type, activity.object_type, activity.object_label, activity.summary, *activity.workflow_hints]))
    blocked_terms = tuple(term for term in sorted(BLOCKED_TEXT_TERMS) if term in text)
    if blocked_terms:
        return "blocked", tuple(f'text_match="{term}"' for term in blocked_terms[:3])
    if {"meeting", "calendar", "transcript", "minutes"} & hints or "meeting" in text:
        return "meeting", _classification_signals(activity, hints, ("meeting", "calendar", "transcript", "minutes"), ("meeting",), ("meeting", "calendar_event"))
    if {"status", "report", "weekly-update"} & hints or "status" in text:
        return "status", _classification_signals(activity, hints, ("status", "report", "weekly-update"), ("status",), ())
    if {"sales", "crm", "lead", "account", "prospect", "outreach", "customer-call"} & hints or any(term in text for term in ("sales", "crm", "lead", "account brief", "prospect", "outreach")):
        return "sales", _classification_signals(activity, hints, ("sales", "crm", "lead", "account", "prospect", "outreach", "customer-call"), ("sales", "crm", "lead", "account brief", "prospect", "outreach"), ())
    if {"support", "customer-success", "escalation", "helpdesk", "zendesk"} & hints or any(term in text for term in ("support", "customer success", "escalation", "helpdesk", "zendesk")):
        return "support", _classification_signals(activity, hints, ("support", "customer-success", "escalation", "helpdesk", "zendesk"), ("support", "customer success", "escalation", "helpdesk", "zendesk"), ())
    if {"release", "changelog", "pull-request", "pr", "merge-request"} & hints or any(term in text for term in ("release note", "changelog", "pull request", "merge request")):
        return "release", _classification_signals(activity, hints, ("release", "changelog", "pull-request", "pr", "merge-request"), ("release note", "changelog", "pull request", "merge request"), ())
    if {"content", "marketing", "social", "newsletter", "seo", "blog", "article"} & hints or any(term in text for term in ("content", "marketing", "social post", "newsletter", "seo", "blog", "article")):
        return "content", _classification_signals(activity, hints, ("content", "marketing", "social", "newsletter", "seo", "blog", "article"), ("content", "marketing", "social post", "newsletter", "seo", "blog", "article"), ())
    if {"research", "competitor", "market", "company-research", "news"} & hints or any(term in text for term in ("research", "competitor", "market", "company research", "news tracker")):
        return "research", _classification_signals(activity, hints, ("research", "competitor", "market", "company-research", "news"), ("research", "competitor", "market", "company research", "news tracker"), ())
    if {"email", "inbox"} & hints or activity.object_type == "email":
        return "email", _classification_signals(activity, hints, ("email", "inbox"), (), ("email",))
    if {"project", "task", "ticket", "open-loop"} & hints or activity.object_type in {"ticket", "task"}:
        return "project", _classification_signals(activity, hints, ("project", "task", "ticket", "open-loop"), (), ("ticket", "task"))
    if {"decision", "memo", "strategy"} & hints or "decision" in text:
        return "decision", _classification_signals(activity, hints, ("decision", "memo", "strategy"), ("decision",), ())
    return "default", ('fallback="default"',)


def _classification_signals(
    activity: Activity,
    hints: set[str],
    hint_terms: tuple[str, ...],
    text_terms: tuple[str, ...],
    object_types: tuple[str, ...],
) -> tuple[str, ...]:
    text = normalize_match_text(" ".join([activity.activity_type, activity.object_type, activity.object_label, activity.summary, *activity.workflow_hints]))
    signals: list[str] = []
    signals.extend(f'workflow_hint="{hint}"' for hint in sorted(hints & set(hint_terms)))
    signals.extend(f'text_match="{term}"' for term in text_terms if term in text)
    if activity.object_type in object_types:
        signals.append(f'object_type="{activity.object_type}"')
    return tuple(signals) or ('heuristic="text"',)


def normalize_match_text(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", value.lower()).strip()


def generate_proposals(sources: list[Source], activities: list[Activity], limit: int = 3) -> list[Proposal]:
    return list(generate_proposal_batch(sources, activities, limit=limit).selected)


def generate_proposal_batch(sources: list[Source], activities: list[Activity], limit: int = 3) -> ProposalBatch:
    limit = max(0, min(3, limit))
    allowed_sources = approved_source_ids(sources)
    classifications = {id(activity): classify_activity(activity) for activity in activities}
    usable = [
        activity
        for activity in activities
        if (
            activity.source_id in allowed_sources
            and activity.privacy_class not in BLOCKED_PRIVACY_CLASSES
            and classifications[id(activity)][0] != "blocked"
        )
    ]
    if not usable:
        return ProposalBatch((), ())

    grouped: dict[str, list[Activity]] = defaultdict(list)
    for activity in usable:
        grouped[classifications[id(activity)][0]].append(activity)

    ranked_patterns = sorted(
        grouped.items(),
        key=lambda item: (len(item[1]), sum(activity.confidence for activity in item[1])),
        reverse=True,
    )

    proposals = tuple(
        _proposal_from_pattern(pattern, pattern_activities, sources, classifications)
        for pattern, pattern_activities in ranked_patterns
    )
    return ProposalBatch(
        selected=proposals[:limit],
        rejected=tuple(_with_dropped_reason(proposal) for proposal in proposals[limit:]),
    )


def _proposal_from_pattern(
    pattern: str,
    pattern_activities: list[Activity],
    sources: list[Source],
    classifications: dict[int, tuple[str, tuple[str, ...]]],
) -> Proposal:
    template = ROLE_TEMPLATES.get(pattern, ROLE_TEMPLATES["default"])
    source_counts = Counter(activity.source_id for activity in pattern_activities)
    evidence_notes = tuple(
        _evidence_note(activity, classifications.get(id(activity), classify_activity(activity))) for activity in pattern_activities[:5]
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
    scorecard_details = (
        _frequency_detail(pattern_activities),
        _repeatability_detail(pattern_activities),
        _source_quality_detail(source_scores),
        _risk_detail(pattern, source_scores, risk_level),
    )
    return Proposal(
        agent_slug=slug,
        agent_name=agent_name,
        mission=template["mission"],
        pattern=pattern,
        confidence=_confidence(avg_confidence, len(pattern_activities), source_quality),
        opportunity_score=opportunity_score,
        scorecard=tuple(_scorecard_line(item) for item in scorecard_details) + (f"Expected first useful output: {template['actions'][0]}.",),
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
        scorecard_details=scorecard_details,
        confidence_breakdown=_confidence_breakdown(avg_confidence, len(pattern_activities), source_scores),
    )


def _with_dropped_reason(proposal: Proposal) -> Proposal:
    reasons = []
    if proposal.evidence_count < 3:
        noun = "record" if proposal.evidence_count == 1 else "records"
        reasons.append(f"frequency too low ({proposal.evidence_count} {noun})")
    if len(proposal.source_ids) < 2:
        reasons.append("only 1 source")
    if proposal.opportunity_score < 3:
        reasons.append("opportunity score below threshold")
    return Proposal(**{**proposal.__dict__, "dropped_reason": "; ".join(reasons) or "lower ranked than selected recommendations"})


def _scorecard_line(item: ScorecardDetail) -> str:
    return f"{item.label}: {item.score}/{item.max_score} {item.summary}"


def _frequency_detail(activities: list[Activity]) -> ScorecardDetail:
    return ScorecardDetail(
        label="Frequency",
        score=_frequency_score(activities),
        max_score=5,
        summary=f"based on {len(activities)} evidence records in the lookback window.",
        details=(f"{len(activities)} activity record(s) matched this pattern.",),
    )


def _repeatability_detail(activities: list[Activity]) -> ScorecardDetail:
    hints = Counter(hint for activity in activities for hint in activity.workflow_hints)
    object_types = Counter(activity.object_type for activity in activities)
    labels = Counter(normalize_match_text(activity.object_label) for activity in activities if activity.object_label)
    details: list[str] = []
    if hints:
        hint, count = hints.most_common(1)[0]
        details.append(f'{count} of {len(activities)} activities share workflow_hint: "{hint}"')
    if object_types:
        object_type, count = object_types.most_common(1)[0]
        details.append(f'{count} of {len(activities)} share object_type: "{object_type}"')
    recurring = [(label, count) for label, count in labels.most_common() if count > 1]
    if recurring:
        label, count = recurring[0]
        details.append(f'Recurring title: "{label}" appeared {count}x')
    if not details:
        details.append("No repeated hints, object types, or labels found.")
    return ScorecardDetail(
        label="Repeatability",
        score=_repeatability(activities),
        max_score=5,
        summary="based on recurring work artifacts and workflow hints.",
        details=tuple(details),
    )


def _source_quality_detail(scores: list[SourceScore]) -> ScorecardDetail:
    if scores:
        details = tuple(f"{score.source_id}: {score.status} ({score.score:.2f})" for score in scores)
    else:
        details = ("No approved source scores were available.",)
    return ScorecardDetail(
        label="Source quality",
        score=_source_quality(scores),
        max_score=5,
        summary="based on approved, read-only source scores.",
        details=details,
    )


def _risk_detail(pattern: str, scores: list[SourceScore], risk_level: str) -> ScorecardDetail:
    details = [f'pattern="{pattern}" starts draft-only and human-reviewed.']
    limited_sources = [score.source_id for score in scores if score.status == "limited"]
    if limited_sources:
        details.append(f"Limited source(s): {', '.join(limited_sources)}.")
    if pattern in {"email", "decision"}:
        details.append("Pattern may involve external communication or judgment, so review gates stay strict.")
    return ScorecardDetail(
        label="Risk",
        score={"low": 5, "medium": 3, "high": 1}.get(risk_level, 3),
        max_score=5,
        summary=f"{risk_level}; recommended first version stays draft-only and human-reviewed.",
        details=tuple(details),
    )


def _confidence_breakdown(avg_confidence: float, evidence_count: int, source_scores: list[SourceScore]) -> tuple[str, ...]:
    evidence_weight = 0.62
    if evidence_count >= 8:
        evidence_weight = 0.92
    elif evidence_count >= 5:
        evidence_weight = 0.86
    elif evidence_count >= 3:
        evidence_weight = 0.78
    elif evidence_count >= 2:
        evidence_weight = 0.70
    source_quality = sum(score.score for score in source_scores) / len(source_scores) if source_scores else 0.0
    return (
        f"Avg activity confidence: {avg_confidence:.2f} from source metadata.",
        f"Evidence count weight: {evidence_weight:.2f} from {evidence_count} record(s).",
        f"Source quality: {source_quality:.2f} average approved-source score.",
    )


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


def _evidence_note(activity: Activity, classification: tuple[str, tuple[str, ...]]) -> EvidenceNote:
    locator = f" ({activity.locator})" if activity.locator else ""
    label = activity.object_label.replace("\n", " ").strip()
    summary = activity.summary.replace("\n", " ").strip()
    if len(summary) > 180:
        summary = summary[:177].rstrip() + "..."
    pattern, signals = classification
    return EvidenceNote(
        text=f"{activity.occurred_at}: {activity.activity_type} {activity.object_type} '{label}' - {summary}{locator}",
        classified_as=pattern,
        classification_signals=signals,
    )
