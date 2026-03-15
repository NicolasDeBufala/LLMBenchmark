from pydantic import BaseModel
from src.schemas.Schema import Schema
from src.schemas.RawPBIExposure import RawPBIExposure as PB
import json

class PBISemanticModelSchema(Schema):

    idSchema: str = "pbi_semantic_model"

    def __init__(self):
        super().__init__(self.idSchema)

    def load_content(self, content: str) -> BaseModel:
        data = json.loads(content)
        data = data.get("DATASETTMSLJSON", data)
        pbi_semantic_model: PB = PB.from_json(data)
        return pbi_semantic_model