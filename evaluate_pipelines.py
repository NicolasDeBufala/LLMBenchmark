"""
Pipeline Evaluation Script with CSV-based Score Caching

This script:
1. Loads existing scores from score.csv
2. Analyzes all CV folders in outputFiles
3. Loads corresponding targets from targetFiles
4. Scores files (skipping cached scores unless outdated)
5. Saves results to score.csv
6. Analyzes and ranks pipelines by average score

Usage:
    python evaluate_pipelines.py
"""

import os
import sys
import json
import csv
from pathlib import Path
from datetime import datetime
from collections import defaultdict
import statistics
import traceback

# Add project to path
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.append(PROJECT_ROOT)

from src.inputFiles.FileManager import FileManager
from src.schemas.SchemaManager import SchemaManager
from src.schemas.CvSchema import CvSchema
from src.target.Target import Target
from src.scoring.BaseModels.CV.CvModelScoringFunction import CvModelScoringFunction
from src.schemas.CvModel import CVData


class PipelineEvaluator:
    """Manages pipeline evaluation with CSV caching"""
    
    def __init__(self, dataset_folder: str, score_csv_path: str = "score.csv"):
        """
        Initialize evaluator
        
        Args:
            dataset_folder: Path to cvProAIAnnotatedCV folder
            score_csv_path: Path to score.csv file
        """
        self.dataset_folder = dataset_folder
        self.score_csv_path = score_csv_path
        self.output_folder = os.path.join(dataset_folder, "outputFiles")
        self.target_folder = os.path.join(dataset_folder, "targetFiles")
        
        # Initialize managers
        self.file_manager = FileManager()
        self.schema_manager = SchemaManager()
        self.schema_manager.addSchema(CvSchema())
        self.scorer = CvModelScoringFunction(logging=False)
        
        # Load existing scores
        self.scores_cache = {}
        self.load_score_csv()
        
        # Track new scores to be added (for periodic CSV updates)
        self.pending_writes = []
        self.write_batch_size = 5
        
    def load_score_csv(self):
        """Load existing scores from CSV into memory"""
        if not os.path.exists(self.score_csv_path):
            print(f"Score CSV not found at {self.score_csv_path}, will create new one")
            return
        
        try:
            with open(self.score_csv_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    key = row.get("fileName")
                    if key:
                        # Convert timestamp back to datetime
                        if row.get("timestamp"):
                            row["timestamp_dt"] = datetime.fromisoformat(row["timestamp"])
                        self.scores_cache[key] = row
            print(f"✓ Loaded {len(self.scores_cache)} existing scores from {self.score_csv_path}")
        except Exception as e:
            print(f"Error loading score CSV: {e}")
    
    def flush_csv_writes(self):
        """Append pending writes to CSV"""
        if not self.pending_writes:
            return
        
        # fieldnames = [
        #     "fileName", "CV_id", "model_id", "prompt_id", "transformationProcessId",
        #     "isError", "errorType", "errorDetail","score_average",
        #     "scoreTarget1", "scoreTarget2", "scoreTarget3",
        #     "timestamp"
        # ]
        fieldnames = ["fileName", "CV_id", "model_id", "prompt_id", "transformationProcessId", "isError","errorType","errorDetail","timestamp","scoreTarget1","scoreTarget2","scoreTarget3","scoreAverage","score_poste","score_introduction","score_seniority","score_missions","score_languages","score_educations","score_certifications","score_skills","score_activity_domains"]
        # fieldnames = list(self.pending_writes[0].keys())
        
        try:
            # Check if file exists to determine write mode
            file_exists = os.path.exists(self.score_csv_path)
            
            
            with open(self.score_csv_path, 'a', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                
                # Write header only if file doesn't exist
                if not file_exists:
                    writer.writeheader()
                
                # Write pending entries
                for score_entry in self.pending_writes:
                    entry_copy = score_entry.copy()
                    if "timestamp_dt" in entry_copy:
                        del entry_copy["timestamp_dt"]
                    writer.writerow(entry_copy)
            
            self.pending_writes.clear()
        except Exception as e:
            print(f"Error writing to CSV: {e}")
    
    def save_score_csv(self):
        """Flush all pending writes and save final CSV"""
        # Flush any remaining writes
        self.flush_csv_writes()
        print(f"✓ Final CSV saved to {self.score_csv_path}")
    
    def needs_rescoring(self, file_path: str, cache_entry: dict) -> bool:
        """Check if a file needs rescoring based on timestamp"""
        if not cache_entry:
            return True
        
        try:
            file_mtime = os.path.getmtime(file_path)
            file_mtime_dt = datetime.fromtimestamp(file_mtime)
            
            cached_timestamp = cache_entry.get("timestamp_dt")
            if cached_timestamp is None and cache_entry.get("timestamp"):
                cached_timestamp = datetime.fromisoformat(cache_entry["timestamp"])
            
            if cached_timestamp is None:
                return True
            
            # Rescore if file was modified after the cached score
            return file_mtime_dt > cached_timestamp
        except Exception as e:
            print(f"  Warning: Error checking timestamp for {file_path}: {e}")
            return False
    
    def parse_filename(self, filename: str) -> dict:
        """
        Parse filename to extract pipeline components
        
        Format: CV_{cv_num}_{reader_id}_{model_id}_{prompt_id}_{iteration}.json
        Example: CV_98_15_azaf-deepSeek-V3.2_korSkeletonCVPromptHeader_2.json
        
        Returns:
        - reader_id (transformation process id)
        - model_id (can contain hyphens)
        - prompt_id (camelCase or compound)
        - iteration
        """
        try:
            base_name = filename.replace('.json', '')
            parts = base_name.split('_')
            
            if len(parts) < 5:
                return {
                    "transformation_id": None,
                    "model_id": None,
                    "prompt_id": None,
                    "iteration": None
                }
            
            # parts[0] = "CV"
            # parts[1] = cv number
            # parts[2] = reader_id (the transformation process id)
            transformation_id = parts[2]
            
            # parts[3] onward = model_id, prompt_id, iteration
            # The last part is the iteration number
            iteration = parts[-1]
            
            # Everything between reader_id and iteration becomes model_id and prompt_id
            remaining_parts = parts[3:-1]  # Everything between reader_id and iteration
            
            if len(remaining_parts) == 1:
                # Only one part between reader and iteration - it's the model_id
                model_id = remaining_parts[0]
                prompt_id = None
            elif len(remaining_parts) >= 2:
                # Last part before iteration is prompt_id, rest is model_id
                model_id = '_'.join(remaining_parts[:-1])
                prompt_id = remaining_parts[-1]
            else:
                model_id = None
                prompt_id = None
            
            return {
                "transformation_id": transformation_id,
                "model_id": model_id,
                "prompt_id": prompt_id,
                "iteration": iteration
            }
        except Exception as e:
            print(f"  Warning: Could not parse filename {filename}: {e}")
        
        return {
            "transformation_id": None,
            "model_id": None,
            "prompt_id": None,
            "iteration": None
        }
        
    
    def score_file(self, file_path: str, cv_id: str, target_objects: list) -> dict:
        """
        Score a single file against all targets
        
        Returns:
            dict with score data and error info
        """
        result = {
            "isError": False,
            "errorType": None,
            "errorDetail": None,
            "scores": [],
            "scores_detailed": []
        }
        
        try:
            # Load JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check for parse errors
            if "_parse_error" in data:
                result["isError"] = True
                result["errorType"] = "Parse Error"
                result["errorDetail"] = data.get("_parse_error", "Unknown parse error")
                return result
            
            # Unwrap if wrapped
            if "extractCvInfo" in data:
                data = data["extractCvInfo"]
            
            # Convert to CVData model (this validates during conversion)
            try:
                cv_data = CVData.from_json(data)
            except TypeError as te:
                # If from_json expects string, convert to JSON string
                if "json" in str(te).lower():
                    cv_data = CVData.from_json(json.dumps(data))
                else:
                    raise
            
            if cv_data is None:
                result["isError"] = True
                result["errorType"] = "Validation Error"
                result["errorDetail"] = "Failed to create CV data model from content"
                return result
            
            # Score against each target
            for target_obj in target_objects:
                score = self.scorer.score_verbose(cv_data, target_obj)
                result["scores"].append(score[0])
                result["scores_detailed"].append(score[1])
                # print("Result : ",score)
            
        except json.JSONDecodeError as e:
            result["isError"] = True
            result["errorType"] = "JSON Parse Error"
            result["errorDetail"] = str(e)
        except Exception as e:
            result["isError"] = True
            result["errorType"] = "Processing Error"
            result["errorDetail"] = str(e)
        
        return result
    
    def evaluate_cv_folder(self, cv_id: str, output_folder: str, target_objects: list):
        """
        Evaluate all files in a CV output folder
        
        Args:
            cv_id: CV identifier (e.g., "CV_5")
            output_folder: Path to the output folder
            target_objects: List of target objects for scoring
        """
        if not os.path.exists(output_folder):
            print(f"  ⚠ Output folder not found: {output_folder}")
            return
        
        # Get all items in directory
        all_items = os.listdir(output_folder)
        
        # Filter for JSON files (case-insensitive)
        files = sorted([f for f in all_items if f.lower().endswith('.json')])
        
        if not files:
            print(f"  ⚠ No JSON files found in {output_folder}")
            return
        
        print(f"\n  Processing {len(files)} files...")
        
        for file_idx, filename in enumerate(files, 1):
            file_path = os.path.join(output_folder, filename)
            
            # Check cache
            cache_entry = self.scores_cache.get(filename)
            
            if cache_entry and not self.needs_rescoring(file_path, cache_entry):
                # Use cached score
                continue
            
            # Parse filename to get pipeline components
            parsed = self.parse_filename(filename)
            
            # Score the file
            score_result = self.score_file(file_path, cv_id, target_objects)
            
            # Create CSV entry
            csv_entry = {
                "fileName": filename,
                "CV_id": cv_id,
                "model_id": parsed["model_id"],
                "prompt_id": parsed["prompt_id"],
                "transformationProcessId": parsed["transformation_id"],
                "isError": str(score_result["isError"]),
                "errorType": score_result["errorType"] or "",
                "errorDetail": score_result["errorDetail"] or "",
                "timestamp": datetime.now().isoformat()
            }
            
            # Add individual target scores
            for idx, score in enumerate(score_result["scores"][:3], 1):
                csv_entry[f"scoreTarget{idx}"] = f"{score:.6f}"
            # Pad missing target scores
            for idx in range(len(score_result["scores"]) + 1, 4):
                csv_entry[f"scoreTarget{idx}"] = ""

            # Average score
            if score_result["scores"]:
                avg_score = sum(score_result["scores"]) / len(score_result["scores"])
                csv_entry["scoreAverage"] = f"{avg_score:.6f}"
                if score_result["scores_detailed"]:
                    for field in score_result["scores_detailed"][0].keys():
                        field_scores = [d.get(field, 0) for d in score_result["scores_detailed"]]
                        avg_field_score = sum(field_scores) / len(field_scores)
                        csv_entry[f"score_{field}"] = f"{avg_field_score:.6f}"
                else:
                    for field in ['score_introduction', 'score_activity_domains', 'score_poste', 'score_languages', 'score_missions', 'score_certifications', 'score_skills', 'score_educations', 'score_seniority']:
                        csv_entry[f"{field}"] = ""
            else:
                csv_entry["scoreAverage"] = ""
                for field in ['score_introduction', 'score_activity_domains', 'score_poste', 'score_languages', 'score_missions', 'score_certifications', 'score_skills', 'score_educations', 'score_seniority']:
                    csv_entry[f"{field}"] = ""

            # Update cache and pending writes
            self.scores_cache[filename] = csv_entry
            self.pending_writes.append(csv_entry)
            
            # Flush to CSV periodically
            if len(self.pending_writes) >= self.write_batch_size or file_idx == len(files):
                self.flush_csv_writes()
                print(f"    Processed {file_idx}/{len(files)} files - CSV updated")
            elif file_idx % 10 == 0:
                print(f"    Processed {file_idx}/{len(files)} files")
    
    def run_evaluation(self):
        """Run full evaluation pipeline"""
        print("=" * 120)
        print("PIPELINE EVALUATION - START")
        print("=" * 120)
        
        if not os.path.exists(self.output_folder):
            print(f"Error: Output folder not found: {self.output_folder}")
            return False
        
        # Find all CV folders
        cv_folders = []
        for item in os.listdir(self.output_folder):
            item_path = os.path.join(self.output_folder, item)
            if os.path.isdir(item_path) and item.startswith("CV_"):
                cv_folders.append(item)
        
        cv_folders = sorted(cv_folders)
        print(f"\nFound {len(cv_folders)} CV folders to evaluate")
        
        # Evaluate each CV folder
        for cv_idx, cv_id in enumerate(cv_folders, 1):
            print(f"\n[{cv_idx}/{len(cv_folders)}] Evaluating {cv_id}...")
            
            # Load targets
            target_folder_path = os.path.join(self.target_folder, cv_id)
            
            try:
                target = Target("", cv_id, "cv")
                target.setTargets(self.dataset_folder, self.schema_manager, nested=False, verbose=False)
                target_objects = target.targetData
                
                if not target_objects:
                    print(f"  ⚠ No targets found for {cv_id}")
                    continue
                
                print(f"  Loaded {len(target_objects)} targets")
                
            except Exception as e:
                print(f"  ⚠ Error loading targets for {cv_id}: {e}")
                continue
            
            # Evaluate output folder
            cv_output_folder = os.path.join(self.output_folder, cv_id)
            self.evaluate_cv_folder(cv_id, cv_output_folder, target_objects)
        
        # Save results (flush any remaining writes)
        print(f"\n{'=' * 120}")
        print(f"SAVING RESULTS")
        print(f"{'=' * 120}")
        print(f"Total scores in CSV: {len(self.scores_cache)}")
        self.save_score_csv()
        
        # Analyze pipelines
        self.analyze_pipelines()
        
        return True
    
    def analyze_pipelines(self):
        """Analyze and rank pipelines based on scores"""
        print(f"\n{'=' * 120}")
        print("PIPELINE ANALYSIS - RANKING BY AVERAGE SCORE")
        print(f"{'=' * 120}")
        
        pipeline_data = defaultdict(lambda: {
            "scores": [],
            "error_count": 0,
            "valid_count": 0,
            "pipelines": []  # Store individual entries for debugging
        })
        
        # Aggregate scores by pipeline
        for filename, entry in self.scores_cache.items():
            if entry.get("isError") == "True":
                # Build pipeline key
                model_id = entry.get("model_id", "unknown")
                prompt_id = entry.get("prompt_id", "unknown")
                transformation_id = entry.get("transformationProcessId", "unknown")
                pipeline_key = f"{model_id}_{transformation_id}_{prompt_id}"
                
                pipeline_data[pipeline_key]["error_count"] += 1
            else:
                # Extract scores
                scores = []
                for idx in range(1, 4):
                    score_str = entry.get(f"scoreTarget{idx}", "").strip()
                    if score_str:
                        try:
                            scores.append(float(score_str))
                        except ValueError:
                            pass
                
                if scores:
                    # Build pipeline key
                    model_id = entry.get("model_id", "unknown")
                    prompt_id = entry.get("prompt_id", "unknown")
                    transformation_id = entry.get("transformationProcessId", "unknown")
                    pipeline_key = f"{model_id}_{transformation_id}_{prompt_id}"
                    
                    avg_score = sum(scores) / len(scores)
                    pipeline_data[pipeline_key]["scores"].append(avg_score)
                    pipeline_data[pipeline_key]["valid_count"] += 1
                    pipeline_data[pipeline_key]["pipelines"].append({
                        "filename": filename,
                        "cv_id": entry.get("CV_id"),
                        "avg_score": avg_score
                    })
        
        # Sort pipelines by average score
        sorted_pipelines_docx = sorted(
            [it for it in pipeline_data.items() if it[0].split("_")[1] in ["101", "102"]],
            key=lambda x: (
                sum(x[1]["scores"]) / len(x[1]["scores"]) if x[1]["scores"] else 0
            ),
            reverse=True
        )

        sorted_pipelines_pdf = sorted(
            [it for it in pipeline_data.items() if it[0].split("_")[1] not in ["101", "102"]],
            key=lambda x: (
                sum(x[1]["scores"]) / len(x[1]["scores"]) if x[1]["scores"] else 0
            ),
            reverse=True
        )
        
        # Print detailed results
        print(f"\n{'Rank':<6} {'Pipeline':<50} {'Avg Score':<12} {'Valid':<8} {'Errors':<8} {'Error %':<10} {'Std Dev':<10}")
        print("-" * 120)
        
        for rank, (pipeline_key, data) in enumerate(sorted_pipelines_docx, 1):
            scores = data["scores"]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)
            else:
                avg_score = std_dev = min_score = max_score = 0
            
            error_count = data["error_count"]
            valid_count = data["valid_count"]
            total_count = valid_count + error_count
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            print(f"{rank:<6} {pipeline_key:<50} {avg_score:<12.6f} {valid_count:<8} {error_count:<8} {error_rate:<10.1f} {std_dev:<10.6f}")
        
        # Print detailed summary for top pipelines
        print(f"\n{'=' * 120}")
        print("DETAILED PIPELINE ANALYSIS")
        print(f"{'=' * 120}")
        
        for rank, (pipeline_key, data) in enumerate(sorted_pipelines_docx[:10], 1):
            scores = data["scores"]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)
            else:
                avg_score = std_dev = min_score = max_score = 0
            
            error_count = data["error_count"]
            valid_count = data["valid_count"]
            total_count = valid_count + error_count
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            print(f"\n{rank}. Pipeline: {pipeline_key}")
            print(f"   Average Score:      {avg_score:.6f}")
            print(f"   Valid Outputs:      {valid_count}")
            print(f"   Error Outputs:      {error_count} ({error_rate:.1f}%)")
            print(f"   Score Range:        min={min_score:.6f}, max={max_score:.6f}")
            print(f"   Std Deviation:      {std_dev:.6f}")
            print(f"   Total Samples:      {total_count}")
        
        print(f"\n{'Rank':<6} {'Pipeline':<50} {'Avg Score':<12} {'Valid':<8} {'Errors':<8} {'Error %':<10} {'Std Dev':<10}")
        print("-" * 120)
        
        for rank, (pipeline_key, data) in enumerate(sorted_pipelines_pdf, 1):
            scores = data["scores"]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)
            else:
                avg_score = std_dev = min_score = max_score = 0
            
            error_count = data["error_count"]
            valid_count = data["valid_count"]
            total_count = valid_count + error_count
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            print(f"{rank:<6} {pipeline_key:<50} {avg_score:<12.6f} {valid_count:<8} {error_count:<8} {error_rate:<10.1f} {std_dev:<10.6f}")
        
        # Print detailed summary for top pipelines
        print(f"\n{'=' * 120}")
        print("DETAILED PIPELINE ANALYSIS")
        print(f"{'=' * 120}")
        
        for rank, (pipeline_key, data) in enumerate(sorted_pipelines_pdf[:10], 1):
            scores = data["scores"]
            
            if scores:
                avg_score = sum(scores) / len(scores)
                std_dev = statistics.stdev(scores) if len(scores) > 1 else 0
                min_score = min(scores)
                max_score = max(scores)
            else:
                avg_score = std_dev = min_score = max_score = 0
            
            error_count = data["error_count"]
            valid_count = data["valid_count"]
            total_count = valid_count + error_count
            error_rate = (error_count / total_count * 100) if total_count > 0 else 0
            
            print(f"\n{rank}. Pipeline: {pipeline_key}")
            print(f"   Average Score:      {avg_score:.6f}")
            print(f"   Valid Outputs:      {valid_count}")
            print(f"   Error Outputs:      {error_count} ({error_rate:.1f}%)")
            print(f"   Score Range:        min={min_score:.6f}, max={max_score:.6f}")
            print(f"   Std Deviation:      {std_dev:.6f}")
            print(f"   Total Samples:      {total_count}")
        

        print(f"\n{'=' * 120}")
        print("EVALUATION COMPLETE")
        print(f"{'=' * 120}")


def main():
    """Main entry point"""
    try:
        # Setup paths
        dataset_folder = os.path.join("dataset", "cvProAIAnnotatedCV")
        score_csv_path = "score.csv"
        
        # Validate dataset folder exists
        if not os.path.exists(dataset_folder):
            print(f"Error: Dataset folder not found: {dataset_folder}")
            print(f"Current directory: {os.getcwd()}")
            return 1
        
        # Run evaluation
        evaluator = PipelineEvaluator(dataset_folder, score_csv_path)
        success = evaluator.run_evaluation()
        
        return 0 if success else 1
        
    except Exception as e:
        print(f"\nFatal error: {e}")
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
