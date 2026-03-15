from pydantic import BaseModel

class PBISemanticModel(BaseModel):


    tables: list
    relationships: list
    measures: list
    columns: list

    #placeholder code
    
    @classmethod
    def from_json(cls, data: dict):
        return cls(
            tables=data.get("tables", []),
            relationships=data.get("relationships", []),
            measures=data.get("measures", []),
            columns=data.get("columns", [])
        )


