from kor.prompts import create_langchain_prompt
from kor.encoders import initialize_encoder
from kor.type_descriptors import initialize_type_descriptors
from src.prompts.PromptBaseClass import PromptBaseClass
from src.prompts.KorCv import resume_schema, clone_kor_object

class PromptSkeletonCv(PromptBaseClass):

    def __init__(self, idSchema: str):
        super().__init__(idSchema, "korSkeletonCVPromptHeader")

    def get_kor_cv_prompt(self) -> tuple[str, str]:
        skeleton_schema = clone_kor_object(resume_schema, keepExamples=False, keepDescription=False)
        prompt = create_langchain_prompt(
            skeleton_schema,  # Remove examples from the schema
            initialize_encoder("json", skeleton_schema),
            initialize_type_descriptors("typescript"),
            validator=None,
            instruction_template=None,
            input_formatter="triple_quotes",
        )
        return "Tu vas recevoir un CV dont on a besoin d'extraire les informations en suivant un schéma précis qui va t'être décrit" \
            ". Essaie de remplir au mieux les informations du CV." + \
            prompt.to_string(""), "KorResumerSchemaNoExamplesNorDescriptionPrompt"
    
    def get_prompt(self, option: str = "") -> tuple[str, str]:
        return self.get_kor_cv_prompt()