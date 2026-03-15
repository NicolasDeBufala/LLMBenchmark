import os

from pydantic import BaseModel
from src.prompts.PromptBaseClass import PromptBaseClass
from src.outputFiles.OutputFile import OutputFile
from src.inputFiles.EntryFile import EntryFile
from src.inputFiles.PDFFile import PDFFile
from src.inputFiles.DocXFile import DocXFile
from src.inputFiles.TxtFile import TxtFile
from src.inputFiles.TextContent import TextContent
from src.inputFiles.CodeMFile import CodeMFile
from src.llm.LLMCallBaseClass import LLMCallBaseClass
from src.schemas.Schema import Schema
from typing import List, Dict, Union
import os

class FileManager():

    fileDict: dict[str, EntryFile] = {}

    def __init__(self, fileDict: dict = None):
        """
        Initialize the FileManager with a dictionary of files.
        """
        self.fileDict = fileDict if fileDict is not None else {}

    def get_file_list(self) -> List[EntryFile]:
        """
        Get the list of files.
        """
        return list(self.fileDict.values())
    
    def add_folder(self, folder: str) -> None:
        """
        Add a folder to the file manager.
        """
        # Check folder content

        # Add all files to fileDict
        entryFile_folder_path = os.path.join(folder, "entryFiles")
        print("Reading folder :", entryFile_folder_path)
        for file in os.listdir(entryFile_folder_path):
            id = file.split(".")[0]
            if file.endswith(".docx"):
                self.fileDict[id] = DocXFile(id, os.path.join(entryFile_folder_path, file), [])
            elif file.endswith(".pdf"):
                self.fileDict[id] = PDFFile(id, os.path.join(entryFile_folder_path, file), [])
            elif file.endswith(".txt"):
                with open(os.path.join(entryFile_folder_path, file), 'r') as f:
                    content = f.read()
                self.fileDict[id] = TextContent(id, os.path.join(entryFile_folder_path, file), content, [])
            elif file.endswith(".json"):
                self.fileDict[id] = CodeMFile(id, os.path.join(entryFile_folder_path, file), [])

            else:
                continue
                # raise NameError("File unknown: " + file)
            self.fileDict[id].folder = folder
            
    @classmethod
    def get_entryfile(cls, id: str, file: str) -> EntryFile:
        """
        Add a file to the file manager.
        """
        print("Reading file :", file, id)
        if file.endswith(".docx"):
            return DocXFile(id, file, [])
        elif file.endswith(".pdf"):
            return PDFFile(id, file, [])
        elif file.endswith(".txt"):
            with open(file, 'r', encoding="utf-8") as f:
                content = f.read()
            return TextContent(id, file, content, [])
        else:
            raise NameError("File unknown: " + file)

    def get_entry(self, id: str) -> EntryFile:
        """
        Get an entry file by its ID.
        """
        if id in self.fileDict:
            return self.fileDict[id]
        else:
            raise NameError("File unknown: " + id)

    def get_output_path(self, outputFile: OutputFile) -> str:
        """
        Get the output path for a file.
        """
        if outputFile.idEntryFile in self.fileDict:
            return self.fileDict[outputFile.idEntryFile].get_output_path()
        else:
            raise NameError("File unknown: " + outputFile.idEntryFile)

    def get_nb_outputs(self, outputPath: str, transformationProcessID: str, promptID: str, llmID: str) -> int:
        """
        Get the number of outputs for a file.
        """
        pattern = "_" + "_".join([transformationProcessID, llmID, promptID]) + "_"
        print("Checking outputs : ", outputPath, pattern)
        if os.path.exists(outputPath):
            return len([name for name in os.listdir(outputPath) if name.endswith(".json") and pattern in name])
        else:
            return 0
        
    def get_outputs_of_pipeline(self, outputPath: str, transformationProcessID: str, promptID: str, llmID: str, schema: Schema) -> list[BaseModel]:
        """
        Get the number of outputs for a file.
        """
        pattern = "_" + "_".join([transformationProcessID, llmID, promptID]) + "_"
        print("Checking outputs : ", outputPath, pattern)
        if os.path.exists(outputPath):
            results = [name for name in os.listdir(outputPath) if name.endswith(".json") and "__" + id + "__" in name and pattern in name]
            loaded_results = [schema.load_content(open(os.path.join(outputPath, name), 'r').read()) for name in results]
            return loaded_results
        else:
            return []
        
    def get_outputs(self, outputPath: str, id: str, schema: Schema) -> list[BaseModel]:
        """
        Get the number of outputs for a file.
        """
        print("Checking outputs : ", outputPath, id)
        if os.path.exists(outputPath):
            results = [name for name in os.listdir(outputPath) if name.endswith(".json") and name.startswith(id + "_")]
            print(results)
            loaded_results = [schema.load_content(open(os.path.join(outputPath, name), 'r', encoding="utf-8").read()) for name in results]
            print(loaded_results)
            return loaded_results
        else:
            print("No outputs found for path: ", outputPath)
            return []
        
    def save_output_file(self, outputFile: OutputFile, nbDone: int, schema: Schema, transformationProcessID: str, prompt: PromptBaseClass, llm: LLMCallBaseClass) -> None:
        """
        Save the output file.
        """
        if outputFile.idEntryFile in self.fileDict:
            outputPath = self.fileDict[outputFile.idEntryFile].get_output_path()
            if not os.path.exists(outputPath):
                os.makedirs(outputPath)
            # print(outputPath)
            # print(outputFile.content)
            # print(type(outputFile.content))
            json_content: BaseModel = schema.load_content(outputFile.content)
            # print(type(json_content))
            outputFile.save(os.path.join(outputPath, "_".join([outputFile.idEntryFile, transformationProcessID, llm.idModel, prompt.id, str(nbDone)]) + ".json"), json_content.model_dump_json(indent=2))
        else:
            raise NameError("File unknown: " + outputFile.idEntryFile)