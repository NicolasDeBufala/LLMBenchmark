from kor.prompts import create_langchain_prompt
from kor.encoders import initialize_encoder
from kor.type_descriptors import initialize_type_descriptors
from src.prompts.PromptBaseClass import PromptBaseClass
from src.prompts.KorCv import resume_schema, clone_kor_object

class PromptNaifCv(PromptBaseClass):

    def __init__(self, idSchema: str):
        super().__init__(idSchema, "korNaifCVPromptHeader")


    def get_kor_cv_prompt(self) -> tuple[str, str]:
        example_less_schema = clone_kor_object(resume_schema, keepExamples=False, keepDescription=True)
        prompt = create_langchain_prompt(
            example_less_schema,  # Remove examples from the schema
            initialize_encoder("json", example_less_schema),
            initialize_type_descriptors("typescript"),
            validator=None,
            instruction_template=None,
            input_formatter="triple_quotes",
        )
        return "Tu vas recevoir un CV dont on a besoin d'extraire les informations en suivant un schéma précis qui va t'être décrit" \
            ". Essaie de remplir au mieux les informations du CV. Le résultat doit être un JSON valide, conforme au schéma défini plus bas." + \
            prompt.to_string(""), "KorResumerSchemaNoExamplesPrompt"
    
    def get_prompt(self, option: str = "") -> tuple[str, str]:
        return self.get_kor_cv_prompt()