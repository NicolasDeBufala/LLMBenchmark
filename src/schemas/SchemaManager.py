from typing import List
from src.schemas.Schema import Schema

class SchemaManager:

    schemaDict: dict

    def __init__(self):
        self.schemaDict = {}

    def addSchema(self, schema: Schema):
        self.schemaDict[schema.id] = schema

    def getSchema(self, id: str) -> Schema:
        if id in self.schemaDict:
            return self.schemaDict[id]
        else:
            raise NameError("Schema unknown " + id)

    def get_schema_list(self) -> List[Schema]:
        return self.schemaDict.values()
