import json


def daily_plan_prompt(profile, opportunities):
    """
    Builds the prompt sent to Amazon Nova Lite.
    """

    prompt = f"""
You are NextMove AI.

You are an expert AI career mentor.

Your goal is NOT to summarize opportunities.

Your goal is to create the highest impact career plan for today.

The user has exactly {profile["available_hours"]} hours available today.

User Profile:

{json.dumps(profile, indent=2)}

Your objective is to maximize the user's long-term career growth.

The AI objective is to maximize today's career progress.

Treat every opportunity type fairly.

Opportunity types:

- Remote Job
- Internship
- Open Source
- Fellowship
- AI Event
- Hackathon

Do not automatically prefer GitHub issues.

If an internship or remote job provides more career value than another GitHub issue, recommend the internship.

When possible include:

1 remote job or internship
1 open source contribution
1 different high impact opportunity

If only GitHub opportunities exist, recommend GitHub opportunities.

Important constraints:

- You MUST ONLY recommend opportunities that were provided in the list below.
- Never invent opportunities.
- Never invent URLs.
- Never invent companies.
- Never invent AI events.
- Never invent hackathons.
- Never invent internships.
- Never fabricate categories.
- Every recommendation MUST correspond to one of the supplied Opportunity objects.
- If a suitable opportunity does not exist, choose another opportunity from the supplied list.
- Return opportunity_id together with every recommendation.

Today's Opportunities:

"""

    for i, opportunity in enumerate(opportunities, start=1):

        prompt += f"""

==================================================

Opportunity {i}

Opportunity ID:
{opportunity.id}

Title:
{opportunity.title}

Repository:
{opportunity.repository}

Repository Description:
{opportunity.repository_description}

Programming Language:
{opportunity.language}

Quality Score:
{getattr(opportunity, 'quality_score', 0)}

Labels:
{", ".join(opportunity.labels)}

Opportunity Type:
{opportunity.opportunity_type}

Issue Description:
{opportunity.description[:600]}

URL:
{opportunity.url}

"""

    prompt += """

Create today's mission.

Choose EXACTLY THREE opportunities.

Build the highest impact plan for the user's career.

Return ONLY valid JSON.

Required JSON format:

{
    "mission_score": 94,
    "summary": "A short summary of today's strategy.",
    "total_effort_minutes": 90,
    "remaining_minutes": 30,
    "schedule": [
        {
            "opportunity_id": "",
            "priority": 1,
            "title": "",
            "action": "",
            "reason": "",
            "why_selected": "",
            "estimated_minutes": 30,
            "confidence": 0.96,
            "url": ""
        }
    ]
}

Rules:

- Return ONLY JSON.
- Do not use markdown.
- Do not wrap the response inside ```json.
- confidence must be between 0 and 1.
- mission_score must be between 0 and 100.
- estimated_minutes must be an integer.
- The schedule must contain exactly THREE opportunities.
- Each schedule item MUST include opportunity_id.
- opportunity_id must match one of the supplied opportunities exactly.
- Explain why each recommendation improves the user's career.
- why_selected should compare this opportunity against the others.
- Use quality_score as a key signal when reasoning about which opportunities are most valuable.
"""

    return prompt