from providers.base import BaseProvider
from models.opportunity import Opportunity
import os
from datetime import datetime, timezone

import requests
from dotenv import load_dotenv

load_dotenv()

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}

if GITHUB_TOKEN:
    HEADERS["Authorization"] = f"Bearer {GITHUB_TOKEN}"



class GitHubProvider(BaseProvider):

    SEARCH_URL = "https://api.github.com/search/issues"
    ALLOWED_LANGUAGES = {"Python", "JavaScript", "TypeScript", "Go", "Java", "Rust"}
    RELEVANT_KEYWORDS = [
        "ai",
        "software engineering",
        "software",
        "full stack",
        "backend",
        "frontend",
        "cloud",
        "devops",
        "open source",
        "machine learning",
    ]
    IRRELEVANT_KEYWORDS = [
        "chemistry",
        "biology",
        "medical",
        "physics",
        "finance research",
        "agriculture",
        "academic research",
        "documentation",
        "docs",
    ]

    def get_repository_details(self, repository_url: str):
        response = requests.get(repository_url, headers=HEADERS, timeout=15)
        response.raise_for_status()
        return response.json()

    def fetch(self):
        params = {
            "q": 'label:"good first issue" state:open',
            "sort": "updated",
            "order": "desc",
            "per_page": 20,
        }

        response = requests.get(self.SEARCH_URL, params=params, headers=HEADERS, timeout=15)
        response.raise_for_status()

        data = response.json()

        opportunities = []

        for issue in data.get("items", []):
            repo = self.get_repository_details(issue["repository_url"])

            if not self._is_relevant_repository(repo, issue):
                continue

            opportunities.append(
                Opportunity(
                    id=str(issue.get("id") or ""),
                    title=issue.get("title") or "",
                    description=issue.get("body") or "",
                    source="GitHub",
                    url=issue.get("html_url") or "",
                    opportunity_type="Open Source",
                    repository=repo.get("full_name") or "",
                    repository_description=repo.get("description") or "",
                    language=repo.get("language"),
                    stars=repo.get("stargazers_count") or 0,
                    labels=[label.get("name") for label in issue.get("labels", []) if label.get("name")],
                    tags=[label.get("name") for label in issue.get("labels", []) if label.get("name")],
                    quality_score=self._calculate_quality_score(repo, issue),
                )
            )

        return opportunities[:20]

    def _is_relevant_repository(self, repo, issue) -> bool:
        text = " ".join([
            repo.get("full_name") or "",
            repo.get("description") or "",
            issue.get("title") or "",
            issue.get("body") or "",
        ]).lower()

        if any(keyword in text for keyword in self.IRRELEVANT_KEYWORDS):
            return False

        if not any(keyword in text for keyword in self.RELEVANT_KEYWORDS):
            return False

        language = (repo.get("language") or "").strip()
        return language in self.ALLOWED_LANGUAGES

    def _calculate_quality_score(self, repo, issue) -> int:
        score = 0
        stars = repo.get("stargazers_count") or 0
        score += min(int(stars / 100), 30)

        labels = [label.get("name", "").lower() for label in issue.get("labels", []) if label.get("name")]
        if any("good first issue" in label for label in labels):
            score += 25
        if any("help wanted" in label for label in labels):
            score += 15

        activity_value = repo.get("updated_at") or repo.get("pushed_at")
        if activity_value:
            try:
                updated_at = datetime.fromisoformat(activity_value.replace("Z", "+00:00"))
                age_days = (datetime.now(timezone.utc) - updated_at).days
                score += 20 if age_days < 180 else 5
            except ValueError:
                score += 5

        if (repo.get("language") or "") in self.ALLOWED_LANGUAGES:
            score += 15

        return min(score, 100)