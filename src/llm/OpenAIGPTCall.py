from src.llm.LLMCallBaseClass import LLMCallBaseClass, remove_trailing_commas
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass
from src.outputFiles.OutputFile import OutputFile
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback


from src.Environnement  import getConfig

class OpenAIGPTCall(LLMCallBaseClass):
    """
    Class to call the OpenAI GPT model.
    """

    def __init__(self, idModel: str="gpt-4o-mini", deploymentName = "", apiVersion: str= "2024-04-01-preview", options: List[str] = []):
        super().__init__(options)
        self.idModel = idModel
        self.deploymentName = self.idModel if deploymentName == "" else deploymentName
        self.apiVersion = apiVersion
        self.entryFileFormatAccepted = [True, False, False, False]

    def inner_generate_response(self, entryFile: EntryFile, prompt: PromptBaseClass, overridedEntryFileID: str = "") -> OutputFile:

        endpoint = getConfig("OPENAI_API_BASE") + "openai/deployments/" + self.deploymentName + "/chat/completions?api-version=" + self.apiVersion
        # print("Endpoint : " + endpoint)
        # print("oldEndpoint : " + getConfig("OPENAI_ENDPOINT"))
        llm: AzureChatOpenAI = AzureChatOpenAI(
            azure_endpoint=endpoint,
            openai_api_version=self.apiVersion,
            deployment_name=self.idModel,
            openai_api_type="azure",
            api_key=getConfig("OPENAI_API_KEY"),
            temperature=0.1
        )

        prompt_message = prompt.get_prompt()[0]
        # print(type(prompt_message))
        mess1 = SystemMessage(prompt_message)
        # mess2 = HumanMessage("\"\"\" "+ entryFile.get_text() + " \"\"\"""")
        mess2 = HumanMessage("### RESUME START ###\n" + entryFile.get_text() + "\n### RESUME END ###")
        result_message = llm.invoke([mess1, mess2])
        metrics={}
        with get_openai_callback() as cb:
            result_message = llm.invoke([mess1, mess2])
            metrics=cb
        # print(metrics)
        # print(result_message)
        if result_message.content.startswith("<json>") and result_message.content.endswith("</json>"):
            result_message.content = result_message.content[6:-7].strip()
        # print(result_message.content)
        result_message.content = remove_trailing_commas(result_message.content)
        # print(result_message.content)
        return OutputFile(
            idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
            idPrompt=prompt.id,
            idSchema=prompt.idSchema,
            idLLM=self.idModel,
            content=result_message.content,
            metrics=metrics
        )
