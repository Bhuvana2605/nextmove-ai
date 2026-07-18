import re
from html import unescape

import requests

from providers.base import BaseProvider
from models.opportunity import Opportunity


class RemoteOKProvider(BaseProvider):

    JOBS_URL = "https://remoteok.com/api"

    def fetch(self) -> list[Opportunity]:
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json",
        }

        response = requests.get(self.JOBS_URL, headers=headers, timeout=15)
        response.raise_for_status()

        payload = response.json()

        if isinstance(payload, dict):
            jobs = payload.get("jobs") or payload.get("results") or []
        elif isinstance(payload, list):
            jobs = payload
        else:
            jobs = []

        opportunities = []

        for job in jobs:
            if not isinstance(job, dict):
                continue

            if "position" not in job:
                continue

            if not self._is_english_job(job):
                continue

            if not self._is_relevant_job(job):
                continue

            tags = self._collect_tags(job)
            language = self._extract_language(tags)

            company = job.get("company") or {}
            if not isinstance(company, dict):
                company = {}

            repository = (
                company.get("name")
                or job.get("company_name")
                or job.get("company")
                or ""
            )
            repository_description = (
                company.get("description")
                or job.get("company_description")
                or ""
            )

            opportunities.append(
                Opportunity(
                    id=str(job.get("id") or job.get("slug") or job.get("position") or ""),
                    title=job.get("position") or job.get("title") or "",
                    description=self._strip_html(job.get("description") or job.get("description_html") or ""),
                    source="RemoteOK",
                    url=job.get("url") or job.get("apply_url") or "",
                    opportunity_type="Remote Job",
                    repository=str(repository) if repository is not None else "",
                    repository_description=str(repository_description) if repository_description is not None else "",
                    language=language,
                    stars=0,
                    labels=tags,
                    tags=tags,
                    deadline=None,
                    location="Remote",
                    quality_score=self._calculate_quality_score(job),
                )
            )

        return opportunities[:20]

    def _collect_tags(self, job: dict) -> list[str]:
        tags = []

        for field_name in ("tags", "technologies", "categories"):
            value = job.get(field_name)

            if isinstance(value, str):
                tags.extend(self._normalize_tags(value))
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, str):
                        tags.append(item.strip())
                    elif isinstance(item, dict):
                        name = item.get("name") or item.get("label") or ""
                        if isinstance(name, str) and name.strip():
                            tags.append(name.strip())

        return [tag for tag in tags if isinstance(tag, str) and tag.strip()]

    def _normalize_tags(self, value: str) -> list[str]:
        return [
            item.strip()
            for item in value.replace("|", ",").split(",")
            if item.strip()
        ]

    def _extract_language(self, tags: list[str]) -> str | None:
        known_keywords = [
            "python",
            "javascript",
            "typescript",
            "react",
            "node",
            "java",
            "go",
            "rust",
            "php",
            "docker",
            "aws",
            "azure",
            "kubernetes",
            "postgres",
            "mysql",
            "sql",
            "mongodb",
            "redis",
            "terraform",
        ]

        for tag in tags:
            lower = tag.lower()
            if any(keyword in lower for keyword in known_keywords):
                return tag

        return None

    def _is_relevant_job(self, job: dict) -> bool:
        text = " ".join([
            self._strip_html(job.get("position") or job.get("title") or ""),
            self._strip_html(job.get("description") or job.get("description_html") or ""),
            " ".join(self._collect_tags(job)),
        ]).lower()

        include_keywords = [
            "software engineer",
            "software",
            "developer",
            "engineer",
            "backend",
            "frontend",
            "full stack",
            "fullstack",
            "python",
            "javascript",
            "typescript",
            "react",
            "node",
            "node.js",
            "java",
            "go",
            "rust",
            "ai",
            "machine learning",
            "llm",
            "data",
            "cloud",
            "aws",
            "internship",
            "intern",
            "graduate",
            "entry level",
            "junior",
            "associate",
            "trainee",
        ]

        exclude_keywords = [
            "sales",
            "marketing",
            "hr",
            "customer support",
            "customer success",
            "recruiter",
            "medical",
            "finance",
            "legal",
            "real estate",
            "merchandiser",
            "director",
            "vice president",
            "vp",
            "principal",
            "staff engineer",
        ]

        if any(word in text for word in exclude_keywords):
            return False

        return any(word in text for word in include_keywords)

    def _is_english_job(self, job: dict) -> bool:
        title = self._strip_html(job.get("position") or job.get("title") or "")
        description = self._strip_html(job.get("description") or job.get("description_html") or "")
        tags = " ".join(self._collect_tags(job))
        text = " ".join([title, description, tags]).lower()

        if not text:
            return True

        if not re.search(r"[a-z]", text):
            return False

        english_keywords = {
            "the",
            "and",
            "for",
            "with",
            "team",
            "work",
            "remote",
            "software",
            "developer",
            "engineer",
            "backend",
            "frontend",
            "full",
            "stack",
            "python",
            "javascript",
            "typescript",
            "react",
            "node",
            "java",
            "go",
            "rust",
            "ai",
            "machine",
            "learning",
            "ml",
            "data",
            "cloud",
            "aws",
            "intern",
            "internship",
            "graduate",
            "entry",
            "level",
            "junior",
            "associate",
            "trainee",
            "build",
            "develop",
            "design",
            "experience",
            "skills",
            "role",
        }

        words = re.findall(r"[a-z]+", text)
        hits = sum(1 for word in words if word in english_keywords)
        if hits >= 2:
            return True

        return any(keyword in text for keyword in (
            "software",
            "developer",
            "engineer",
            "backend",
            "frontend",
            "full stack",
            "fullstack",
            "python",
            "javascript",
            "typescript",
            "react",
            "node",
            "java",
            "go",
            "rust",
            "ai",
            "machine learning",
            "ml",
            "data",
            "cloud",
            "aws",
            "internship",
            "intern",
            "graduate",
            "entry level",
            "junior",
            "associate",
            "trainee",
        ))

    def _calculate_quality_score(self, job: dict) -> int:
        text = " ".join([
            self._strip_html(job.get("position") or job.get("title") or ""),
            self._strip_html(job.get("description") or job.get("description_html") or ""),
            " ".join(self._collect_tags(job)),
        ]).lower()

        score = 0
        if any(keyword in text for keyword in ("internship", "intern")):
            score += 25
        if any(keyword in text for keyword in ("junior", "entry level", "graduate", "associate", "trainee")):
            score += 20
        if any(keyword in text for keyword in ("ai", "machine learning", "llm", "generative ai")):
            score += 20
        if "python" in text:
            score += 15
        if any(keyword in text for keyword in ("aws", "cloud")):
            score += 15
        if "remote" in text:
            score += 5
        return min(score, 100)

    def _strip_html(self, value: str | None) -> str:
        if not value:
            return ""

        text = str(value)
        text = re.sub(r"<[^>]+>", " ", text)
        text = unescape(text)
        text = re.sub(r"&nbsp;", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()