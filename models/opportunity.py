from dataclasses import dataclass
from typing import Optional


@dataclass
class Opportunity:

    id: str

    title: str

    description: str

    source: str

    url: str

    opportunity_type: str

    repository: str

    repository_description: str

    language: Optional[str]

    stars: int

    labels: list[str]

    tags: list[str]

    deadline: Optional[str] = None

    location: Optional[str] = None

    quality_score: int = 0