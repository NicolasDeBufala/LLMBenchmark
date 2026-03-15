from pydantic import BaseModel
from src.schemas.Schema import Schema
from src.schemas.CvModel import CVData
import json

class CvSchema(Schema):

    idSchema: str = "cv"

    def __init__(self):
        super().__init__(self.idSchema)

    def load_content(self, content: str) -> BaseModel:
        try:
            data = json.loads(content)
            data = data.get("extractCvInfo", data)
            cv: CVData = CVData.from_json(data)
            return cv
        except Exception as e:
            print(f"Error loading CV content: {e}")
            return None