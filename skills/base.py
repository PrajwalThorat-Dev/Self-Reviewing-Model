from abc import ABC, abstractmethod


class BaseSkill(ABC):
    # every skill must define a name — used for logging and registry lookup
    name: str

    @abstractmethod
    def build_generate_prompt(self, user_input: str) -> str:
        # builds the prompt generate_node sends to the LLM for the first draft
        ...

    @abstractmethod
    def build_critique_prompt(self, user_input: str, draft: str, fact_check_summary: str) -> str:
        # builds the prompt the skill's critique node sends to the LLM
        ...

    @abstractmethod
    def build_refine_prompt(self, user_input: str, draft: str, critique: dict, correction_notes: str) -> str:
        # builds the prompt refine_node sends to the LLM to fix issues
        ...