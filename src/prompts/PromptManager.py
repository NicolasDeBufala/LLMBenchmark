from typing import List
from src.prompts.PromptBaseClass import PromptBaseClass

class PromptManager:
    """
    Manages the prompts.
    """

    promptDict: dict[str, PromptBaseClass] = {}

    def __init__(self):
        """
        Initialize the PromptManager with a prompt ID, metrics, content, and an optional date.
        """
        self.promptDict = {}

    def add_prompt(self, prompt_id: str, prompt: PromptBaseClass) -> None:
        """
        Add a prompt to the manager.
        """
        self.promptDict[prompt_id] = prompt

    def get_prompt(self, prompt_id: str) -> PromptBaseClass:
        """
        Get a prompt by its ID.
        """
        if prompt_id in self.promptDict:
            return self.promptDict[prompt_id]
        else:
            raise NameError("Prompt unknown: " + prompt_id)
        
    def remove_prompt(self, prompt_id: str) -> None:
        """
        Remove a prompt by its ID.
        """
        if prompt_id in self.promptDict:
            del self.promptDict[prompt_id]
        else:
            raise NameError("Prompt unknown: " + prompt_id)
        
    def get_prompt_list(self) -> List[PromptBaseClass]:
        """
        Get the list of prompts.
        """
        return [prompt for prompt in self.promptDict.values() if prompt is not None]