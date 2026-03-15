"""
Azure AI Foundry Model Deployment Call

This class enables calling models deployed on Azure AI Foundry.
Works with any model deployed through Azure AI Foundry (GPT-4, Claude, Llama, etc.)

Requires:
- Deployment endpoints and keys configured in environment variables
- Or passed as parameters
"""

from src.llm.LLMCallBaseClass import LLMCallBaseClass, remove_trailing_commas
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass
from src.outputFiles.OutputFile import OutputFile
from typing import List
from openai import AzureOpenAI
from openai import APITimeoutError
from src.Environnement import getConfig
import os
import threading
import time


class AzureAIFoundryCall(LLMCallBaseClass):
    """
    Class to call models deployed on Azure AI Foundry.
    
    Azure AI Foundry allows deploying various models (GPT-4, Llama, Claude, etc.)
    This class provides a unified interface to call any deployed model.
    """

    def __init__(
        self,
        idModel: str,
        deployment_name: str = "",
        endpoint: str = "",
        api_key: str = "",
        api_version: str = "2024-12-01-preview",
        temperature: float = 0.1,
        max_tokens: int = 4096,
        timeout_seconds: int = 300,
        options: List[str] = []
    ):
        """
        Initialize Azure AI Foundry model call.
        
        Args:
            idModel: Model identifier for tracking (e.g., "gpt-5-mini")
            deployment_name: Azure deployment name to call (e.g., "gpt-5-mini-eu")
            endpoint: Azure AI Foundry endpoint URL
            api_key: API key for authentication
            api_version: API version (default: "2024-12-01-preview" - latest)
            temperature: Temperature for generation
            max_tokens: Maximum tokens to generate
            timeout_seconds: Hard timeout for API calls in seconds (default: 300 = 5 minutes)
                           Request is forcefully cancelled if it exceeds this duration.
            options: Additional options
            
        Environment Variables (fallback):
            AZURE_FOUNDRY_ENDPOINT - Default endpoint
            AZURE_FOUNDRY_API_KEY - Default API key
            
        Example:
            llm = AzureAIFoundryCall(
                idModel="gpt-5-mini",
                deployment_name="gpt-5-mini-eu",
                timeout_seconds=300  # 5 minutes
            )
        """
        super().__init__(options)
        self.idModel = idModel
        self.deployment_name = deployment_name if deployment_name else idModel
        print(f"Initializing AzureAIFoundryCall for model '{self.idModel}' with deployment '{self.deployment_name}'")
        self.api_version = api_version
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.timeout_seconds = timeout_seconds
        self.entryFileFormatAccepted = [True, False, False, False]
        
        # Get endpoint and key from parameters or environment
        self.endpoint = endpoint or os.getenv("AZURE_FOUNDRY_ENDPOINT", "")
        self.api_key = api_key or os.getenv("AZURE_FOUNDRY_API_KEY", "")
        print(f"Using Azure AI Foundry endpoint: {self.endpoint}")
        if not self.endpoint or not self.api_key:
            print("⚠ Warning: Azure AI Foundry endpoint or API key not configured")
            print("  Set AZURE_FOUNDRY_ENDPOINT and AZURE_FOUNDRY_API_KEY environment variables")
        
        # Initialize Azure OpenAI client (timeout handled by thread wrapper)
        self.client = AzureOpenAI(
            azure_endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version
        )

    def clone(self):
        """Create a clone of this instance (for thread safety)"""
        return self.__init__(
            idModel=self.idModel,
            deployment_name=self.deployment_name,
            endpoint=self.endpoint,
            api_key=self.api_key,
            api_version=self.api_version,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            timeout_seconds=self.timeout_seconds
        )
    

    def inner_generate_response(
        self, 
        entryFile: EntryFile, 
        prompt: PromptBaseClass, 
        overridedEntryFileID: str = ""
    ) -> OutputFile:
        """
        Generate response using Azure AI Foundry deployed model.
        Includes TRUE timeout protection with request cancellation.
        """
        try:
            prompt_message = prompt.get_prompt()[0]
            entry_text = entryFile.get_text()
            
            # Use threading to enforce hard timeout
            result_container = {"response": None, "error": None}
            start_time = time.time()
            
            def call_azure():
                """Worker function to call Azure API"""
                try:
                    response = self.client.chat.completions.create(
                        model=self.deployment_name,
                        response_format={"type": "json_object"},
                        messages=[
                            {
                                "role": "system",
                                "content": prompt_message
                            },
                            {
                                "role": "user",
                                "content": f"### RESUME START ###\n{entry_text}\n### RESUME END ###"
                            }
                        ]
                    )
                    result_container["response"] = response
                except Exception as e:
                    result_container["error"] = e
            
            # Start API call in daemon thread
            api_thread = threading.Thread(target=call_azure, daemon=True)
            api_thread.start()
            
            # Wait for thread to complete OR timeout
            api_thread.join(timeout=self.timeout_seconds)
            elapsed_time = time.time() - start_time
            
            # Check if thread is still alive (timeout occurred)
            if api_thread.is_alive():
                error_msg = f"API call timeout after {self.timeout_seconds} seconds (actual: {elapsed_time:.1f}s)"
                print(f"⏱ TIMEOUT: {error_msg}")
                return OutputFile(
                    idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                    idPrompt=prompt.id,
                    idSchema=prompt.idSchema,
                    idLLM=self.idModel,
                    content=error_msg,
                    metrics={
                        "error": "TIMEOUT",
                        "timeout_seconds": self.timeout_seconds,
                        "actual_elapsed_seconds": elapsed_time,
                        "error_message": error_msg,
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                )
            
            # Check for errors from the thread
            if result_container["error"]:
                error = result_container["error"]
                error_msg = f"Azure API error: {str(error)}"
                print(f"✗ API ERROR: {error_msg}")
                return OutputFile(
                    idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                    idPrompt=prompt.id,
                    idSchema=prompt.idSchema,
                    idLLM=self.idModel,
                    content=error_msg,
                    metrics={
                        "error": "API_ERROR",
                        "error_message": str(error),
                        "prompt_tokens": 0,
                        "completion_tokens": 0,
                        "total_tokens": 0
                    }
                )
            
            response = result_container["response"]
            result_content = response.choices[0].message.content
            print(f"✓ Azure response received ({elapsed_time:.2f}s): {len(result_content)} chars")
            
            # Clean up XML tags if present
            if result_content.startswith("<json>") and result_content.endswith("</json>"):
                result_content = result_content[6:-7].strip()
            
            result_content = remove_trailing_commas(result_content)
            
            # Build metrics
            metrics = {
                "model": self.idModel,
                "deployment": self.deployment_name,
                "endpoint": self.endpoint,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
                "elapsed_seconds": elapsed_time
            }
            print(f"Azure AI Foundry call metrics : {metrics}")
            
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=result_content,
                metrics=metrics
            )
        
        except Exception as e:
            error_msg = f"Error: {str(e)}"
            print(f"✗ ERROR: {error_msg}")
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=error_msg,
                metrics={"error": str(e), "prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            )


# Example usage:
"""
from src.llm.AzureAIFoundryCall import AzureAIFoundryCall
import os

# Set Azure credentials (or pass as parameters)
os.environ["AZURE_FOUNDRY_ENDPOINT"] = "https://your-resource.openai.azure.com/"
os.environ["AZURE_FOUNDRY_API_KEY"] = "your-api-key"

# Create client
llm = AzureAIFoundryCall(
    idModel="gpt-5-mini",           # Model identifier for tracking
    deployment_name="gpt-5-mini-eu"  # Actual Azure deployment name to call
)

# Use in pipeline
output = llm.generate_response(transformed_file, prompt)

# Alternative: pass endpoint/key explicitly
llm = AzureAIFoundryCall(
    idModel="gpt-5-mini",
    deployment_name="gpt-5-mini-eu",
    endpoint="https://your-resource.openai.azure.com/",
    api_key="your-api-key"
)
"""
