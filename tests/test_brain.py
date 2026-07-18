import json
from dataclasses import asdict

from providers.github import GitHubProvider
from agent.brain import Brain


provider = GitHubProvider()

brain = Brain()

opportunities = provider.fetch()

plan = brain.create_daily_plan(opportunities)

print(json.dumps(asdict(plan), indent=4))