from dataclasses import dataclass


@dataclass
class PlanItem:
    opportunity_id: str
    priority: int
    title: str
    action: str
    reason: str
    why_selected: str
    estimated_minutes: int
    confidence: float
    url: str

@dataclass
class DailyPlan:
    mission_score: int
    summary: str
    total_effort_minutes: int
    remaining_minutes: int
    schedule: list[PlanItem]