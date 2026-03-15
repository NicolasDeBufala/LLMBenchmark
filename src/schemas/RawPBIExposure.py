from pydantic import BaseModel

class RawPBIExposure(BaseModel):


    content: dict

    def __init__(self, **kwargs):
        if 'content' not in kwargs:
            print("No content provided for RawPBIExposure, initializing with empty dict")
            kwargs['content'] = {}
        super().__init__(**kwargs)
    #placeholder code
    
    @classmethod
    def from_json(cls, data: dict):
        return cls(
            content=data
        )


