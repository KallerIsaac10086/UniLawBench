from pathlib import Path
from typing import Dict, List
import evalscope


def run_evaluation(model_path: Path, dataset_ids: List[str], eval_type: str) -> Dict[str, dict]:
    """
    Execute evaluation pipeline for specified datasets
    
    Args:
        model_path: Local path to model files
        dataset_ids: List of dataset identifiers (e.g. ['1-1', '2-3'])
        eval_type: Evaluation type (mcq/qa)
    
    Returns:
        Dictionary of evaluation results per dataset
    """
    results = {}
    
    for ds_id in dataset_ids:
        try:
            # Load dataset
            data_file = Path(__file__).parent.parent / 'dataset' / eval_type / f"{ds_id}.{'csv' if eval_type == 'mcq' else 'jsonl'}"
            
            # Configure evaluation scope
            scope = evalscope.Scope()
            scope.load_model(str(model_path))
            scope.load_dataset(str(data_file))
            
            # Execute evaluation
            metrics = scope.run()
            results[ds_id] = metrics
            
        except Exception as e:
            raise RuntimeError(f"Evaluation failed for {ds_id}: {str(e)}")
    
    return results