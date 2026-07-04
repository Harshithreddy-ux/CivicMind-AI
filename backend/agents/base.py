from abc import ABC, abstractmethod

class BaseAgent(ABC):
    @abstractmethod
    async def process(self, context: dict) -> dict:
        """
        Process the given context and return a dictionary with the agent's findings.
        Context includes 'query', 'location', etc.
        """
        pass

    def format_error(self, error: Exception) -> dict:
        return {
            "status": "error",
            "message": str(error),
            "data": None
        }

    def format_success(self, data: dict, summary: str = "") -> dict:
        return {
            "status": "success",
            "summary": summary,
            "data": data
        }
