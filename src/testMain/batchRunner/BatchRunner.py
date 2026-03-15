


from typing import List

from src.outputFiles.OutputFile import OutputFile
from src.prompts.PromptManager import PromptManager
from src.inputFiles.FileManager import FileManager
from src.llm.LLMManager import LLMManager
from src.schemas.SchemaManager import SchemaManager
from src.transformation.TransformationProcess import TransformationProcess
from src.transformation.TransformationProcessFactory import TransformationProcessFactory


class BatchRunner:

    def __init__(self, transformationProcesses: List[TransformationProcess], promptManager: PromptManager, fileManager: FileManager, llmManager: LLMManager, schemaManager: SchemaManager, nbRepetitions: int  = 1, nbFailsAuthorizedPerFile: int = 1, fileList: list = []):
        """
        Initialize the BatchRunner with a prompt manager (that contains prompts to use), a file manager (that defines all files to run), 
        and a LLM manager (that defines the LLM to use), and the options for each LLM.
        """

        if transformationProcesses is None:
            raise ValueError("TransformationProcesses cannot be None")
        if promptManager is None:
            raise ValueError("PromptManager cannot be None")
        if fileManager is None:
            raise ValueError("FileManager cannot be None")
        if llmManager is None:
            raise ValueError("LLMManager cannot be None")
        if schemaManager is None:
            raise ValueError("SchemaManager cannot be None")
        if nbRepetitions < 1:
            raise ValueError("Number of repetitions must be at least 1")
        
        if transformationProcesses == []:
            raise ValueError("TransformationProcesses cannot be empty")
        if promptManager.get_prompt_list() == []:
            raise ValueError("PromptManager cannot be empty")
        if fileManager.get_file_list() == []:
            raise ValueError("FileManager cannot be empty")
        if llmManager.get_llm_list() == []:
            raise ValueError("LLMManager cannot be empty")
        if schemaManager.get_schema_list() == []:
            raise ValueError("Schema Manager cannot be empty")
        
        self.transformationProcesses = transformationProcesses
        self.promptManager = promptManager
        self.fileManager = fileManager
        self.llmManager = llmManager
        self.schemaManager = schemaManager
        self.nbRepetitions = nbRepetitions
        self.nbFailsAuthorizedPerFile = nbFailsAuthorizedPerFile
        self.fileList = fileList

        
    def run(self) -> None :
        print(self.fileList)
        for raw_file in self.fileManager.get_file_list():
            print("raw_file : ", raw_file.filename, raw_file.id)
            if self.fileList and raw_file.id in self.fileList:
                print("Processing file : " + raw_file.id)
                for transformationProcess in self.transformationProcesses:
                    #Check if the file is compatible with the transformation process

                    if not transformationProcess.can_run(raw_file):
                        print("File " + raw_file.filename + " is not compatible with transformation process " + str(transformationProcess.idTransformationProcess))
                        continue
                    file = TransformationProcessFactory.get_transformed_entryfile(raw_file.folder, raw_file.id, transformationProcess, raw_file)

                    for llm in self.llmManager.get_llm_list():
                        for prompt in self.promptManager.get_prompt_list():
                            # print(prompt)
                            #Check how many output already stored for this file, prompt, and llm
                            nbDone = 0
                            if file.get_output_path() is not None:
                                nbDone = self.fileManager.get_nb_outputs(file.get_output_path(), str(transformationProcess.idTransformationProcess), prompt.id, llm.idModel)
                                if nbDone >= self.nbRepetitions:
                                    print("Already " + str(nbDone) + " outputs for file " + file.filename + " with prompt " + prompt.id + " and llm " + llm.idModel)
                                    continue
                            nbFails = 0
                            while nbDone < self.nbRepetitions and nbFails < self.nbFailsAuthorizedPerFile:

                                output: OutputFile = llm.generate_response(file, prompt)
                                if output is not None:
                                    nbDone += 1
                                    print(output.content)
                                    self.fileManager.save_output_file(output, nbDone, self.schemaManager.getSchema(output.idSchema), str(transformationProcess.idTransformationProcess), prompt, llm)
                                else:
                                    nbFails += 1
                                    print("Fail "+str(nbFails) + "for file " + file.filename + " with prompt " + prompt.id + " and llm " + llm.idModel)