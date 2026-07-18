import json

from aws.bedrock import invoke
from config import USER_PROFILE
from agent.prompts import daily_plan_prompt

from models.plan import DailyPlan, PlanItem


class Brain:

    def create_daily_plan(self, opportunities):

        prompt = daily_plan_prompt(
            USER_PROFILE,
            opportunities
        )

        try:
            response = invoke(prompt)
        except Exception as exc:
            print(f"Bedrock Error: {exc}")
            return DailyPlan(
                mission_score=0,
                summary="Unable to generate a plan right now.",
                total_effort_minutes=0,
                remaining_minutes=0,
                schedule=[],
            )

        for attempt in range(2):
            try:
                data = json.loads(response)
                break
            except json.JSONDecodeError:
                if attempt == 1:
                    print(response)
                    return DailyPlan(
                        mission_score=0,
                        summary="Unable to generate a valid plan.",
                        total_effort_minutes=0,
                        remaining_minutes=0,
                        schedule=[],
                    )

                prompt += """

Your previous response was not valid JSON.

Return ONLY valid JSON.

Do not use markdown.

Return only the JSON object.
"""
                try:
                    response = invoke(prompt)
                except Exception as exc:
                    print(f"Bedrock Error: {exc}")
                    return DailyPlan(
                        mission_score=0,
                        summary="Unable to generate a plan right now.",
                        total_effort_minutes=0,
                        remaining_minutes=0,
                        schedule=[],
                    )

        schedule = []

        for item in data.get("schedule", []):
            if not isinstance(item, dict):
                continue

            opportunity_id = item.get("opportunity_id") or item.get("id") or ""
            if not opportunity_id and opportunities:
                fallback_index = len(schedule)
                if fallback_index < len(opportunities):
                    opportunity_id = getattr(opportunities[fallback_index], "id", "")

            schedule.append(
                PlanItem(
                    opportunity_id=str(opportunity_id),
                    priority=item.get("priority", 0),
                    title=item.get("title", ""),
                    action=item.get("action", ""),
                    reason=item.get("reason", ""),
                    why_selected=item.get("why_selected", ""),
                    estimated_minutes=item.get("estimated_minutes", 0),
                    confidence=item.get("confidence", 0.0),
                    url=item.get("url", "")
                )
            )

        return DailyPlan(
            mission_score=data.get("mission_score", 0),
            summary=data.get("summary", ""),
            total_effort_minutes=data.get("total_effort_minutes", 0),
            remaining_minutes=data.get("remaining_minutes", 0),
            schedule=schedule
        )