"""
Extraction Pipeline

Orchestrates the complete pipeline:
1. Reader operation (text extraction)
2. LLM processing (with prompt)
3. Output file management

Output format: CVName_TransformationProcessID_ModelIdentifier_promptID_iteration.json
"""

import json
import os
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime

from src.transformation.TransformationProcess import TransformationProcess
from src.prompts.PromptBaseClass import PromptBaseClass
from src.llm.LLMCallBaseClass import LLMCallBaseClass
from src.inputFiles.EntryFile import EntryFile
from src.inputFiles.FileManager import FileManager


class ExtractionPipeline:
    """
    Complete pipeline for CV/Resume extraction.
    
    Combines:
    - Reader operation (TextContent extraction)
    - Prompt template (extraction instructions)
    - LLM (models for extraction)
    
    Output: JSON files with naming convention:
        CVName_TransformationProcessID_ModelIdentifier_promptID_iteration.json
    """
    
    def __init__(
        self,
        transformation_process: TransformationProcess,
        prompt: PromptBaseClass,
        llm: LLMCallBaseClass,
        output_folder: str
    ):
        """
        Initialize the extraction pipeline.
        
        Args:
            transformation_process: Reader operation (e.g., PDFPlumber, PyMuPDF)
            prompt: Prompt template for LLM
            llm: LLM instance for processing
            output_folder: Where to save results
        """
        self.transformation_process = transformation_process
        self.prompt = prompt
        self.llm = llm
        self.output_folder = output_folder
        
        # Create output folder if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
    
    def generate_output_filename(
        self,
        entry_file_name: str,
        transformation_id: int,
        model_id: str,
        prompt_id: str,
        iteration: int
    ) -> str:
        """
        Generate output filename following convention:
        CVName_TransformationProcessID_ModelIdentifier_promptID_iteration.json
        """
        # Clean up filename (remove extension if present)
        cv_name = Path(entry_file_name).stem
        
        filename = f"{cv_name}_{transformation_id}_{model_id}_{prompt_id}_{iteration}.json"
        return filename
    
    def run(
        self,
        entry_file: EntryFile,
        iterations: int = 1,
        save_intermediate: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Run the complete pipeline on an entry file.
        
        Args:
            entry_file: Input file (PDF, DocX, etc.)
            iterations: Number of times to run the pipeline
            save_intermediate: Save extracted text before LLM processing
            
        Returns:
            List of results for each iteration
        """
        results = []
        
        for iteration in range(1, iterations + 1):
            print(f"\n{'='*80}")
            print(f"Pipeline Iteration {iteration}/{iterations}")
            print(f"File: {entry_file.id}")
            print(f"{'='*80}")
            
            try:
                # Step 1: Extract text using reader operation
                print(f"[1/3] Extracting text with {self.transformation_process.idTransformationProcess}...", end=" ")
                extracted_file = self.transformation_process.run(entry_file)
                extracted_text = extracted_file.get_text()
                print(f"✓ ({len(extracted_text)} chars)")
                
                # Step 2: Send to LLM with prompt
                print(f"[2/3] Processing with LLM {self.llm.idModel}...", end=" ")
                llm_output = self.llm.generate_response(extracted_file, self.prompt)
                print("✓")
                
                # Step 3: Prepare and save output
                output_filename = self.generate_output_filename(
                    entry_file.filename,
                    self.transformation_process.idTransformationProcess,
                    self.llm.idModel,
                    self.prompt.id,
                    iteration
                )
                output_path = os.path.join(self.output_folder, output_filename)
                
                # Build result dictionary
                result = {
                    "metadata": {
                        "entry_file": entry_file.id,
                        "filename": output_filename,
                        "timestamp": datetime.now().isoformat(),
                        "iteration": iteration,
                        "reader_operation": self.transformation_process.idTransformationProcess,
                        "model": self.llm.idModel,
                        "prompt_id": self.prompt.id,
                    },
                    "extraction": {
                        "extracted_text_length": len(extracted_text),
                        "extracted_preview": extracted_text[:200] + "..." if len(extracted_text) > 200 else extracted_text,
                    },
                    "llm_response": {
                        "content": llm_output.content,
                        "metrics": llm_output.metrics if hasattr(llm_output, 'metrics') else {},
                    }
                }
                
                # Save to JSON file
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(result, f, indent=2, ensure_ascii=False)
                
                print(f"[3/3] Saving output...", end=" ")
                print(f"✓ ({output_path})")
                
                results.append(result)
                
            except Exception as e:
                error_result = {
                    "metadata": {
                        "entry_file": entry_file.id,
                        "timestamp": datetime.now().isoformat(),
                        "iteration": iteration,
                        "error": str(e),
                    },
                    "status": "FAILED"
                }
                results.append(error_result)
                print(f"✗ Error: {str(e)}")
        
        return results
    
    def run_batch(
        self,
        entry_files: List[EntryFile],
        iterations: int = 1
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run pipeline on multiple files.
        
        Args:
            entry_files: List of input files
            iterations: Iterations per file
            
        Returns:
            Dictionary with results for each file
        """
        batch_results = {}
        
        print(f"\n{'='*80}")
        print(f"Batch Processing: {len(entry_files)} files × {iterations} iterations")
        print(f"{'='*80}\n")
        
        for idx, entry_file in enumerate(entry_files, 1):
            print(f"\n[{idx}/{len(entry_files)}] Processing {entry_file.id}...")
            file_results = self.run(entry_file, iterations)
            batch_results[entry_file.id] = file_results
        
        return batch_results


class PipelineBuilder:
    """
    Builder class for easy pipeline creation and configuration.
    """
    
    def __init__(self, output_folder: str):
        self.output_folder = output_folder
        self.transformation_process = None
        self.prompt = None
        self.llm = None
    
    def set_reader(self, transformation_process: TransformationProcess) -> 'PipelineBuilder':
        """Set the reader operation."""
        self.transformation_process = transformation_process
        return self
    
    def set_prompt(self, prompt: PromptBaseClass) -> 'PipelineBuilder':
        """Set the prompt."""
        self.prompt = prompt
        return self
    
    def set_llm(self, llm: LLMCallBaseClass) -> 'PipelineBuilder':
        """Set the LLM."""
        self.llm = llm
        return self
    
    def build(self) -> ExtractionPipeline:
        """Build the pipeline."""
        if not all([self.transformation_process, self.prompt, self.llm]):
            raise ValueError("Pipeline requires: reader, prompt, and LLM")
        
        return ExtractionPipeline(
            self.transformation_process,
            self.prompt,
            self.llm,
            self.output_folder
        )


# Example usage:
"""
from src.transformation.TransformationProcessFactory import TransformationProcessFactory
from src.llm.LiteLLMOpenAICompatibleCall import LiteLLMOpenAICompatibleCall
from src.prompts.PromptCv import PromptCv
from src.llm.PipelineOrchestrator import PipelineBuilder

# Setup
reader = TransformationProcessFactory.createProcess(3)  # PyMuPDF
prompt = PromptCv("cv")
llm = LiteLLMOpenAICompatibleCall("gpt-4", endpoint="...")

# Build pipeline
pipeline = (PipelineBuilder("./output")
    .set_reader(reader)
    .set_prompt(prompt)
    .set_llm(llm)
    .build())

# Run on single file
results = pipeline.run(entry_file, iterations=3)

# Or run batch
batch_results = pipeline.run_batch(entry_files, iterations=3)

# Output files will be named:
# CV001_3_gpt-4_cv_1.json
# CV001_3_gpt-4_cv_2.json
# CV001_3_gpt-4_cv_3.json
"""
