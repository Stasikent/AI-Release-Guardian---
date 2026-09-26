from abc import ABC, abstractmethod
from app.models.ai import AIAnalysis

class LLMProvider(ABC):
    name: str
    model: str

    @abstractmethod
    async def analyze_release(self, facts: dict) -> AIAnalysis:
        raise NotImplementedError
