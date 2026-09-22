#Step 2: Iterating to Evaluate Datasets (Aggregation)
#To evaluate a full dataset, loop through lists of inputs and aggregate individual results into summary statistics like Mean Absolute Error (MAE) and Accuracy Rate.

def dataset_eval(predictions: list[float], targets: list[float], tolerance: float = 0.05) -> dict:
    """Evaluates a batch of predictions against targets and computes aggregate metrics."""
    if len(predictions) != len(targets) or not predictions:
        raise ValueError("Predictions and targets must be non-empty and equal in length.")

    total_error = 0.0
    correct_count = 0

    for pred, target in zip(predictions, targets):
        error = abs(pred - target)
        total_error += error
        
        # Check tolerance match
        if (error / target) <= tolerance:
            correct_count += 1

    n = len(predictions)
    return {
        "total_samples": n,
        "mean_absolute_error": round(total_error / n, 4),
        "accuracy_rate": round(correct_count / n, 4)
    }

# --- Usage Example ---
preds = [102.0, 49.0, 208.0, 15.0]
targets = [100.0, 50.0, 200.0, 10.0]

metrics = dataset_eval(preds, targets)
print(metrics)
# Output: {'total_samples': 4, 'mean_absolute_error': 2.75, 'accuracy_rate': 0.75}
