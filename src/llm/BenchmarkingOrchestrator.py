"""
Benchmarking Orchestrator

Orchestrates complete benchmarking pipeline with:
- Separate JSON output (only response content)
- Cumulative logging of metrics
- Token tracking
- Response time measurement
- Parse success/failure tracking
"""

import json
import os
import time
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional
from datetime import datetime
from pydantic import ValidationError

from src.transformation.TransformationProcess import TransformationProcess
from src.prompts.PromptBaseClass import PromptBaseClass
from src.llm.LLMCallBaseClass import LLMCallBaseClass
from src.inputFiles.EntryFile import EntryFile
from src.inputFiles.FileManager import FileManager
from src.schemas.CvModel import CVData


class BenchmarkLogger:
    """Handles logging of benchmark metrics"""
    
    def __init__(self, log_file_path: str):
        self.log_file_path = log_file_path
        os.makedirs(os.path.dirname(log_file_path), exist_ok=True)
        
        # Create header if file doesn't exist
        if not os.path.exists(log_file_path):
            self._write_header()
    
    def _write_header(self):
        """Write CSV header"""
        header = "timestamp,entry_file,transformation_id,model,prompt_id,iteration,response_time_s,input_tokens,output_tokens,total_tokens,parse_success,parse_error,extracted_text_length\n"
        with open(self.log_file_path, 'w', encoding='utf-8') as f:
            f.write(header)
    
    def log_call(
        self,
        entry_file_id: str,
        transformation_id: int,
        model_id: str,
        prompt_id: str,
        iteration: int,
        response_time: float,
        input_tokens: int,
        output_tokens: int,
        total_tokens: int,
        parse_success: bool,
        parse_error: str = "",
        extracted_text_length: int = 0
    ):
        """Log a single LLM call"""
        timestamp = datetime.now().isoformat()
        
        log_entry = (
            f"{timestamp},"
            f"{entry_file_id},"
            f"{transformation_id},"
            f"{model_id},"
            f"{prompt_id},"
            f"{iteration},"
            f"{response_time:.3f},"
            f"{input_tokens},"
            f"{output_tokens},"
            f"{total_tokens},"
            f"{str(parse_success)},"
            f'"{parse_error}",'
            f"{extracted_text_length}\n"
        )
        
        # Append to log file
        with open(self.log_file_path, 'a', encoding='utf-8') as f:
            f.write(log_entry)
    
    def print_summary(self):
        """Print summary of logged metrics"""
        try:
            with open(self.log_file_path, 'r') as f:
                lines = f.readlines()
            
            if len(lines) <= 1:
                print("No metrics logged yet")
                return
            
            total_calls = len(lines) - 1
            successful = sum(1 for line in lines[1:] if 'True' in line)
            failed = total_calls - successful
            
            print(f"\nBenchmark Summary:")
            print(f"  Total calls: {total_calls}")
            print(f"  Successful: {successful}")
            print(f"  Failed: {failed}")
            
        except Exception as e:
            print(f"Error reading log: {str(e)}")


class BenchmarkingPipeline:
    """
    Complete benchmarking pipeline with logging.
    
    Separates concerns:
    - Output JSON contains ONLY the extracted content
    - Metrics logged separately to CSV file
    """
    
    def __init__(
        self,
        transformation_process: TransformationProcess,
        prompt: PromptBaseClass,
        llm: LLMCallBaseClass,
        output_folder: str,
        log_file: str
    ):
        self.transformation_process = transformation_process
        self.prompt = prompt
        self.llm = llm
        self.output_folder = output_folder
        self.logger = BenchmarkLogger(log_file)
        
        os.makedirs(output_folder, exist_ok=True)
    
    def generate_output_filename(
        self,
        entry_file_name: str,
        transformation_id: int,
        model_id: str,
        prompt_id: str,
        iteration: int
    ) -> str:
        """Generate output filename"""
        cv_name = Path(entry_file_name).stem
        filename = f"{cv_name}_{transformation_id}_{model_id}_{prompt_id}_{iteration}.json"
        return filename
    
    def _try_parse_json(self, content: str) -> tuple[bool, str]:
        """Try to parse response as JSON"""
        try:
            json.loads(content)
            return True, ""
        except json.JSONDecodeError as e:
            return False, str(e)
    
    def _get_or_create_transformed_file(self, entry_file: EntryFile):
        """
        Check if transformed file exists. If not, create it by running transformation.
        This caching avoids re-running expensive transformations (e.g., Azure OCR).
        
        Args:
            entry_file: Input file to transform
            
        Returns:
            Transformed file (TextContent object)
        """
        # Create transformed files directory
        transformed_dir = os.path.join(
            os.path.dirname(self.output_folder),
            "..",
            "transformedInputFiles"
        )
        os.makedirs(transformed_dir, exist_ok=True)
        
        # Generate transformed file path
        transformation_id = self.transformation_process.idTransformationProcess
        entry_file_stem = Path(entry_file.filename).stem
        transformed_filename = f"{entry_file_stem}_R{transformation_id}.txt"
        transformed_path = os.path.join(transformed_dir, transformed_filename)
        
        # Check if transformed file already exists
        if os.path.exists(transformed_path):
            print(f"    [CACHE HIT] Using cached transformed file: {transformed_filename}")
            with open(transformed_path, 'r', encoding='utf-8') as f:
                content = f.read()
            # Return as TextContent object
            from src.inputFiles.TextContent import TextContent
            return TextContent(entry_file.id, transformed_filename, content)
        
        # Run transformation and save result
        print(f"    [CACHE MISS] Transforming with Reader {transformation_id}...", end=" ", flush=True)
        transformed_file = self.transformation_process.run(entry_file)
        extracted_text = transformed_file.get_text()
        
        # Save transformed file for future use
        with open(transformed_path, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"saved")
        
        return transformed_file
    
    def run(
        self,
        entry_file: EntryFile,
        iterations: int = 1,
        skip_existing: bool = True,
        skip_only_valid_files:bool = False
    ) -> List[Dict[str, Any]]:
        """
        Run benchmarking pipeline.
        
        Args:
            entry_file: Input file
            iterations: Number of iterations
            skip_existing: Skip if output already exists
            
        Returns:
            List of results
        """
        results = []
        
        for iteration in range(1, iterations + 1):
            # Check if output already exists
            output_filename = self.generate_output_filename(
                entry_file.filename,
                self.transformation_process.idTransformationProcess,
                self.llm.idModel,
                self.prompt.id,
                iteration
            )
            output_path = os.path.join(self.output_folder, output_filename)
            if os.path.exists(output_path) and skip_existing:
                if skip_only_valid_files:
                    # Check if existing file is valid JSON
                    try:

                        with open(output_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        if "_parse_error" in data:
                            print(f"  [SKIP] {output_filename} (already exists but is invalid - contains parse error)")
                        else:
                            print(f"  [SKIP] {output_filename} (already exists and is valid)")
                            continue
                    except json.JSONDecodeError:
                        print(f"  [WARNING] {output_filename} already exists but is invalid JSON. It will be overwritten.")
                else:
                    print(f"  [SKIP] {output_filename} (already exists)")
                    continue
            
            try:
                print(f"  [Iter {iteration}] Processing with {self.llm.idModel}...", end=" ", flush=True)
                
                start_time = time.time()
                
                # Step 1: Check or create transformed input file (caching optimization)
                transformed_file = self._get_or_create_transformed_file(entry_file)
                extracted_text = transformed_file.get_text()
                
                # Step 1.5: Check if extracted text is empty/minimal - if so, skip LLM and create empty output
                if not extracted_text or len(extracted_text.strip()) < 100:
                    response_time = time.time() - start_time
                    
                    print(f"[SKIP LLM] Empty input (text_length={len(extracted_text.strip())}, likely scanned PDF)")
                    
                    # Create empty output JSON file with proper template structure
                    empty_output = {
                        "extractCvInfo": {
                            "poste": "",
                            "seniority": 0,
                            "introduction": "",
                            "languages": [],
                            "skillsDomains": [],
                            "educations": [],
                            "certifications": [],
                            "activityDomains": [],
                            "missions": []
                        }
                    }
                    with open(output_path, 'w', encoding='utf-8') as f:
                        json.dump(empty_output, f, indent=2, ensure_ascii=False)
                    
                    # Create raw output file for reference
                    raw_output_folder = self.output_folder.replace("outputFiles", "rawOutputFiles")
                    os.makedirs(raw_output_folder, exist_ok=True)
                    raw_output_path = os.path.join(raw_output_folder, output_filename.replace('.json', '_raw.txt'))
                    with open(raw_output_path, 'w', encoding='utf-8') as f:
                        f.write(f"[EMPTY_INPUT_SKIPPED]\nExtracted text length: {len(extracted_text.strip())}\nText: {extracted_text[:200]}")
                    
                    # Log as skipped due to empty input
                    self.logger.log_call(
                        entry_file_id=entry_file.id,
                        transformation_id=self.transformation_process.idTransformationProcess,
                        model_id=self.llm.idModel,
                        prompt_id=self.prompt.id,
                        iteration=iteration,
                        response_time=response_time,
                        input_tokens=0,
                        output_tokens=0,
                        total_tokens=0,
                        parse_success=False,
                        parse_error="EMPTY_INPUT_FILE - LLM call skipped",
                        extracted_text_length=0
                    )
                    
                    result = {
                        "iteration": iteration,
                        "status": "SKIPPED_EMPTY_INPUT",
                        "response_time": response_time,
                        "total_tokens": 0,
                        "filename": output_filename,
                        "parse_error": "Empty extracted text - likely scanned PDF"
                    }
                    results.append(result)
                    continue
                
                # Step 2: Call LLM
                llm_output = self.llm.generate_response(transformed_file, self.prompt)
                
                response_time = time.time() - start_time
                
                # Step 3: Extract metrics
                metrics = llm_output.metrics if hasattr(llm_output, 'metrics') else {}
                input_tokens = metrics.get('prompt_tokens', 0)
                output_tokens = metrics.get('completion_tokens', 0)
                total_tokens = metrics.get('total_tokens', 0)
                
                # Step 3.5: Check for timeout error
                is_timeout = metrics.get('error') == 'TIMEOUT'
                
                # Step 4: Save raw response BEFORE parsing (for debugging)
                raw_output_folder = self.output_folder.replace("outputFiles", "rawOutputFiles")
                os.makedirs(raw_output_folder, exist_ok=True)
                raw_output_path = os.path.join(raw_output_folder, output_filename.replace('.json', '_raw.txt'))
                with open(raw_output_path, 'w', encoding='utf-8') as f:
                    if is_timeout:
                        f.write(f"[TIMEOUT] API call exceeded {metrics.get('timeout_seconds', '?')} seconds\n")
                        f.write(f"Error: {metrics.get('error_message', 'Unknown')}\n")
                    else:
                        f.write(str(llm_output.content))
                with open(raw_output_path.replace('_raw.txt', '_raw_llm.txt'), 'w', encoding='utf-8') as f:
                    if is_timeout:
                        f.write(f"[TIMEOUT] API call exceeded {metrics.get('timeout_seconds', '?')} seconds\n")
                        f.write(f"Error: {metrics.get('error_message', 'Unknown')}\n")
                    else:
                        f.write(str(llm_output.raw_content_llm))
                
                # Step 5: Parse and validate response
                if is_timeout:
                    parse_success = False
                    parse_error = f"TIMEOUT - API call exceeded {metrics.get('timeout_seconds', '?')} seconds"
                else:
                    parse_success, parse_error = self._try_parse_json(llm_output.content)
                
                # Step 6: Save output (ONLY content, no metadata)
                with open(output_path, 'w', encoding='utf-8') as f:
                    # If timeout occurred, create error output
                    if is_timeout:
                        print(f"    [TIMEOUT ERROR] {parse_error}")
                        content_dict = {
                            "extractCvInfo": {
                                "poste": "",
                                "seniority": 0,
                                "introduction": "",
                                "languages": [],
                                "skillsDomains": [],
                                "educations": [],
                                "certifications": [],
                                "activityDomains": [],
                                "missions": []
                            },
                            "_parse_error": {
                                "error_type": "APITimeout",
                                "error_message": parse_error,
                                "timeout_seconds": metrics.get('timeout_seconds'),
                                "raw_error_detail": metrics.get('error_message', '')
                            }
                        }
                    # If content is a string, parse it first; otherwise use as-is
                    elif isinstance(llm_output.content, str):
                        try:
                            content_dict = json.loads(llm_output.content)
                            # Validate against CVData schema to enforce field types (e.g., seniority: int)
                            extract_info = content_dict.get("extractCvInfo", content_dict)
                            try:
                                validated_cv = CVData.from_json(extract_info)
                                # Re-export with validated data to ensure type coercion/validation applied
                                # Convert back to dict format, excluding internal fields that aren't part of output
                                validated_dict = validated_cv.model_dump(exclude={'comments', 'id_user', 'label', 'status', 'primary_cv', 'id', 'firstname', 'lastname'})
                                content_dict = {"extractCvInfo": validated_dict}
                                # Note: This ensures seniority is coerced to int, languages validated, etc.
                            except ValidationError as val_error:
                                # Validation failed - log it but don't fail completely
                                parse_error = f"Schema validation failed: {str(val_error)[:200]}"
                                print(f"    [VALIDATION ERROR] {parse_error}")
                                parse_success = False
                        except json.JSONDecodeError as json_error:
                            # If not valid JSON, create error structure with diagnostics
                            print(f"    [JSON PARSE ERROR] {str(json_error)[:100]}")
                            content_dict = {
                                "extractCvInfo": {
                                    "poste": "",
                                    "seniority": 0,
                                    "introduction": "",
                                    "languages": [],
                                    "skillsDomains": [],
                                    "educations": [],
                                    "certifications": [],
                                    "activityDomains": [],
                                    "missions": []
                                },
                                "_parse_error": {
                                    "error_type": "JSONDecodeError",
                                    "error_message": str(json_error),
                                    "raw_content_preview": llm_output.content[:500] if llm_output.content else ""
                                }
                            }
                    else:
                        content_dict = llm_output.content
                    json.dump(content_dict, f, indent=2, ensure_ascii=False)
                
                # Step 7: Log metrics
                self.logger.log_call(
                    entry_file_id=entry_file.id,
                    transformation_id=self.transformation_process.idTransformationProcess,
                    model_id=self.llm.idModel,
                    prompt_id=self.prompt.id,
                    iteration=iteration,
                    response_time=response_time,
                    input_tokens=input_tokens,
                    output_tokens=output_tokens,
                    total_tokens=total_tokens,
                    parse_success=parse_success,
                    parse_error=parse_error,
                    extracted_text_length=len(extracted_text)
                )
                
                status = "✓" if parse_success else "✗ (parse failed)"
                print(f"{status} ({response_time:.2f}s, {total_tokens} tokens)")
                
                result = {
                    "iteration": iteration,
                    "status": "SUCCESS" if parse_success else "PARSE_ERROR",
                    "response_time": response_time,
                    "total_tokens": total_tokens,
                    "filename": output_filename,
                    "parse_error": parse_error
                }
                results.append(result)
                
            except Exception as e:
                print(f"✗ ERROR: {str(e)}")
                
                # Log failure
                self.logger.log_call(
                    entry_file_id=entry_file.id,
                    transformation_id=self.transformation_process.idTransformationProcess,
                    model_id=self.llm.idModel,
                    prompt_id=self.prompt.id,
                    iteration=iteration,
                    response_time=0,
                    input_tokens=0,
                    output_tokens=0,
                    total_tokens=0,
                    parse_success=False,
                    parse_error=str(e),
                    extracted_text_length=0
                )
                
                result = {
                    "iteration": iteration,
                    "status": "ERROR",
                    "error": str(e)
                }
                results.append(result)
        
        return results
    
    def run_batch(
        self,
        entry_files: List[EntryFile],
        iterations: int = 1,
        allowed_fails: int = 0
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Run benchmarking on multiple files.
        
        Args:
            entry_files: List of input files
            iterations: Iterations per file
            allowed_fails: Allowed failures per file before skipping
            
        Returns:
            Results dictionary
        """
        batch_results = {}
        
        print(f"\n{'='*80}")
        print(f"Batch Benchmarking: {len(entry_files)} files × {iterations} iterations")
        print(f"{'='*80}\n")
        
        for idx, entry_file in enumerate(entry_files, 1):
            print(f"[{idx}/{len(entry_files)}] {entry_file.id}:")
            
            file_results = self.run(entry_file, iterations=iterations)
            batch_results[entry_file.id] = file_results
            
            # Check failure count
            failures = sum(1 for r in file_results if r['status'] != 'SUCCESS')
            if failures > allowed_fails:
                print(f"  ⚠ Exceeded allowed fails ({failures} > {allowed_fails})")
        
        # Print summary
        self.logger.print_summary()
        
        return batch_results
