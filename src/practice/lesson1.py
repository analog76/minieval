##: Start by writing a function that tests one prediction against one actual value and checks if it falls within an acceptable tolerance.

 
def simple_eval(prediction: float, target: float, tolerance: float = 0.05) -> bool:
    """Evaluates if a single prediction is within a percentage tolerance of the target."""
    error = abs(prediction - target) / target
    return error <= tolerance

# --- Usage Example ---
is_accurate = simple_eval(prediction=102.5, target=100.0, tolerance=0.05)
print("Passes evaluation:", is_accurate)  # Output: True (2.5% error <= 5% tolerance)
