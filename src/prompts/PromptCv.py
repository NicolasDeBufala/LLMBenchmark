from kor.prompts import create_langchain_prompt
from kor.encoders import initialize_encoder
from kor.type_descriptors import initialize_type_descriptors
from src.prompts.PromptBaseClass import PromptBaseClass
from src.prompts.KorCv import resume_schema

class PromptCv(PromptBaseClass):

    def __init__(self, idSchema: str):
        super().__init__(idSchema, "korBaseCVPromptHeader")

    def get_kor_cv_prompt(self) -> tuple[str, str]:
        prompt = create_langchain_prompt(
            resume_schema,
            initialize_encoder("json", resume_schema),
            initialize_type_descriptors("typescript"),
            validator=None,
            instruction_template=None,
            input_formatter="triple_quotes",
        )
        return "Tu vas recevoir un CV dont on a besoin d'extraire les informations en suivant un schéma précis qui va t'être décrit" \
            " et pour lequel tu as des exemples. Ne te limite pas à ces exemples, et essaie de remplir au mieux les informations du CV." + \
            prompt.to_string(""), "KorResumerSchemaPrompt"
    
    def get_prompt(self, option: str = "") -> tuple[str, str]:
        return self.get_kor_cv_prompt()