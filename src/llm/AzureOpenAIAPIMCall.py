from src.llm.LLMCallBaseClass import LLMCallBaseClass, remove_trailing_commas
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass
from src.outputFiles.OutputFile import OutputFile
from typing import List
from langchain_openai import AzureChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_community.callbacks import get_openai_callback


from src.Environnement  import getConfig

class AzureOpenAIAPIMCall(LLMCallBaseClass):
    """
    Class to call the Azure OpenAI GPT model through Azure API Management (APIM).
    """

    def __init__(self, idModel: str="gpt-4.1", deploymentName = "", apiVersion: str= "2024-12-01-preview", options: List[str] = []):
        super().__init__(options)
        self.idModel = idModel
        self.deploymentName = getConfig("AZURE_OPENAI_CHAT_DEPLOYMENT_NAME", self.idModel) if deploymentName == "" else deploymentName
        self.apiVersion = getConfig("AZURE_OPENAI_API_VERSION", apiVersion)
        self.entryFileFormatAccepted = [True, False, False, False]

    def inner_generate_response(self, entryFile: EntryFile, prompt: PromptBaseClass, overridedEntryFileID: str = "") -> OutputFile:

        # Build Azure APIM endpoint for Azure OpenAI
        azure_endpoint = getConfig("AZURE_OPENAI_ENDPOINT")
        endpoint = f"{azure_endpoint}/openai/deployments/{self.deploymentName}/chat/completions?api-version={self.apiVersion}"
        
        print("Using Azure OpenAI deployment: " + self.deploymentName)
        # print("Endpoint : " + endpoint)
        llm: AzureChatOpenAI = AzureChatOpenAI(
            azure_endpoint=azure_endpoint,
            openai_api_version=self.apiVersion,
            deployment_name=self.deploymentName,
            openai_api_type="azure",
            api_key=getConfig("AZURE_OPENAI_API_KEY"),
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
        print("Response received from Azure OpenAI for file : " + entryFile.filename + " " +entryFile.id + " : " + result_message.content[:200])
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
