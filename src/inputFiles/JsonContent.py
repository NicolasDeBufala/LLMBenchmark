from typing import List
from src.inputFiles.EntryFile import EntryFile
import json

class JsonContent(EntryFile):

    formatID: int  = 4
    
    def __init__ (self, id: str, filename:str, content: str, transformationHistory: List[str]= []):
        self.content = content
        super().__init__(id, filename, transformationHistory)

    def save(self, path: str) -> None:
        """
        Save the content to a text file.
        """
        print(self.content)
        try:
            # Try to parse as JSON string first
            formatted_content = json.loads(self.content)
        except json.JSONDecodeError:
            # If that fails, try to evaluate as Python literal (safely)
            try:
                import ast
                formatted_content = ast.literal_eval(self.content)
            except (ValueError, SyntaxError):
                # If all else fails, assume it's already a dict/object
                formatted_content = self.content
        
        with open(path, "w", encoding="utf-8") as f:
            json.dump(formatted_content, f, indent=2)

    def get_text(self) -> str:
        """
        Get the text content.
        """
        return json.dumps(self.content, indent=2)