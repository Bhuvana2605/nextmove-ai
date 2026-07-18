from abc import ABC, abstractmethod
from models.opportunity import Opportunity


class BaseProvider(ABC):

    @abstractmethod
    def fetch(self) -> list[Opportunity]:
        pass