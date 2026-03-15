"""
LiteLLM OpenAI-Compatible Endpoint Call

This class enables calling any OpenAI-compatible LLM endpoint (like LiteLLM, vLLM, etc.)
using the OpenAI API format.

Endpoint: https://litellm.tm.pasapas.org/v1
Library: Uses OpenAI Python client with custom base URL

Example usage:
    llm = LiteLLMOpenAICompatibleCall(
        model_id="gpt-4",
        endpoint="https://litellm.tm.pasapas.org/v1",
        api_key="your-api-key"
    )
"""

from src.llm.LLMCallBaseClass import LLMCallBaseClass, remove_trailing_commas
from src.inputFiles.EntryFile import EntryFile
from src.prompts.PromptBaseClass import PromptBaseClass
from src.outputFiles.OutputFile import OutputFile
from typing import List
from openai import OpenAI, APIConnectionError, APIStatusError
import os


class LiteLLMOpenAICompatibleCall(LLMCallBaseClass):
    """
    Class to call any OpenAI-compatible LLM endpoint (LiteLLM, vLLM, local deployments, etc.)
    
    This allows flexible LLM calling with custom endpoints while maintaining
    the same API interface as other LLM call implementations.
    """

    def __init__(
        self,
        model_id: str,
        endpoint: str,
        api_key: str = None,
        temperature: float = 0.1,
        max_tokens: int = 12000,
        options: List[str] = []
    ):
        """
        Initialize LiteLLM OpenAI-compatible call.
        
        Args:
            model_id: Model identifier (e.g., "gpt-4", "gpt-4-turbo", "claude-3-opus")
            endpoint: OpenAI-compatible endpoint URL (default: litellm sandbox)
            api_key: API key for the endpoint (or set LLM_API_KEY env var)
            temperature: Temperature for generation (0.0 - 2.0)
            max_tokens: Maximum tokens to generate
            options: Additional options
        """
        super().__init__(options)
        self.idModel = model_id
        self.endpoint = endpoint
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.entryFileFormatAccepted = [True, False, False, False]
        
        # Get API key from parameter or environment variable
        self.api_key = api_key or os.getenv("LLM_API_KEY", "placeholder-api-key")
        
        if self.api_key == "placeholder-api-key":
            print(f"⚠ Warning: Using placeholder API key. Set LLM_API_KEY environment variable or pass api_key parameter.")
        
        # Initialize OpenAI client with custom endpoint
        self.client = OpenAI(
            api_key=self.api_key,
            base_url=self.endpoint
        )

    def clone(self):
        """
        Create a clone of this LLM call instance.
        """
        return LiteLLMOpenAICompatibleCall(
            model_id=self.idModel,
            endpoint=self.endpoint,
            api_key=self.api_key,
            temperature=self.temperature,
            max_tokens=self.max_tokens
        )

    def inner_generate_response(
        self, 
        entryFile: EntryFile, 
        prompt: PromptBaseClass, 
        overridedEntryFileID: str = ""
    ) -> OutputFile:
        """
        Generate response using OpenAI-compatible endpoint.
        
        Args:
            entryFile: Input file containing resume/CV text
            prompt: Prompt template for extraction
            overridedEntryFileID: Optional ID override
            
        Returns:
            OutputFile with LLM response
        """
        try:
            # Get prompt and entry file content
            prompt_message = prompt.get_prompt()[0]
            entry_text = entryFile.get_text()
            
            # Format messages
            messages = [
                {
                    "role": "system",
                    "content": prompt_message
                },
                {
                    "role": "user",
                    "content": f"### RESUME START ###\n{entry_text}\n### RESUME END ###"
                }
            ]
            
            # Call LLM endpoint
            response = self.client.chat.completions.create(
                model=self.idModel,
                messages=messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens
            )
            
            # Extract response content
            result_content = response.choices[0].message.content
            raw_response = result_content  # Store raw response for debugging/logging
            
            
            # Clean up XML tags if present
            if result_content.startswith("<json>") and result_content.endswith("</json>"):
                result_content = result_content[6:-7].strip()
            result_content = result_content.strip()
            if result_content[0]  != "{":
                # Remove any leading non-JSON content (e.g., explanations before the JSON)
                json_start = result_content.find("{")
                if json_start != -1:
                    result_content = result_content[json_start:]
                #Remove trailing content after JSON (e.g., explanations after the JSON)
                json_end = result_content.rfind("}")
                if json_end != -1:
                    result_content = result_content[:json_end+1]
             
            # Remove trailing commas for JSON compatibility
            result_content = remove_trailing_commas(result_content)
            
            # Build metrics dictionary
            metrics = {
                "model": self.idModel,
                "endpoint": self.endpoint,
                "prompt_tokens": response.usage.prompt_tokens if response.usage else 0,
                "completion_tokens": response.usage.completion_tokens if response.usage else 0,
                "total_tokens": response.usage.total_tokens if response.usage else 0,
            }
            
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=result_content,
                metrics=metrics,
                raw_content_llm=raw_response
            )
        
        except APIConnectionError as e:
            print(f"Connection error to endpoint {self.endpoint}: {str(e)}")
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=f"Error: Connection failed - {str(e)}",
                metrics={"error": str(e)}
            )
        
        except APIStatusError as e:
            print(f"API error from {self.endpoint}: {str(e)}")
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=f"Error: API error - {str(e)}",
                metrics={"error": str(e)}
            )
        
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return OutputFile(
                idEntryFile=entryFile.id if overridedEntryFileID == "" else overridedEntryFileID,
                idPrompt=prompt.id,
                idSchema=prompt.idSchema,
                idLLM=self.idModel,
                content=f"Error: {str(e)}",
                metrics={"error": str(e)}
            )


# Example usage and documentation
"""
USAGE EXAMPLE:

from src.llm.LiteLLMOpenAICompatibleCall import LiteLLMOpenAICompatibleCall

# Method 1: With explicit API key
llm = LiteLLMOpenAICompatibleCall(
    model_id="gpt-4",
    endpoint="https://litellm.tm.pasapas.org/v1",
    api_key="your-api-key-here"
)

# Method 2: Using environment variable
# Set environment: export LLM_API_KEY="your-api-key"
llm = LiteLLMOpenAICompatibleCall(
    model_id="gpt-4",
    endpoint="https://litellm.tm.pasapas.org/v1"
)

# Method 3: With custom parameters
llm = LiteLLMOpenAICompatibleCall(
    model_id="gpt-4-turbo",
    endpoint="https://litellm.tm.pasapas.org/v1",
    api_key="your-api-key",
    temperature=0.2,
    max_tokens=2048
)

# Add to LLMManager
llmManager = LLMManager()
llmManager.add_llm(llm)

# Use in batch processing
output = llm.generate_response(entryFile, prompt)

COMPATIBLE ENDPOINTS:

1. LiteLLM (Proxy)
   - URL: https://litellm.tm.pasapas.org/v1
   - Supports: OpenAI, Anthropic, Google, Azure, etc.

2. vLLM Local Deployment
   - URL: http://localhost:8000/v1
   - Command: vllm serve meta-llama/Llama-2-7b-hf

3. Ollama
   - URL: http://localhost:11434/v1
   - Requires: ollama pull model-name

4. Azure OpenAI (via proxy)
   - URL: https://api.openai.com/v1
   - With Azure credentials

5. Self-hosted OpenAI-compatible (e.g., LocalAI, text-generation-webui)
   - URL: http://your-server:port/v1
"""
