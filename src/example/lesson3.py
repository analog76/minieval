#Step 3: Making the Eval Function Modular (Custom Rules)
#You can make your evaluator flexible by passing in custom evaluation functions (higher-order functions). This allows you to swap scoring logic without changing the looping code.

from typing import Callable

def modular_eval(data: list[dict], eval_rule: Callable[[dict], float]) -> dict:
    """Applies a customizable evaluation rule over a dataset and returns summary stats."""
    scores = [eval_rule(item) for item in data]
    
    return {
        "count": len(scores),
        "mean_score": round(sum(scores) / len(scores), 4) if scores else 0.0,
        "max_score": max(scores) if scores else 0.0,
        "min_score": min(scores) if scores else 0.0,
    }

# --- Example Rule: Calculate return percentage per trade ---
trades = [
    {"entry": 100, "exit": 110},  # +10%
    {"entry": 50,  "exit": 48},   # -4%
    {"entry": 200, "exit": 230}   # +15%
]

def return_pct_rule(trade: dict) -> float:
    return (trade["exit"] - trade["entry"]) / trade["entry"]

results = modular_eval(trades, return_pct_rule)
print(results)
# Output: {'count': 3, 'mean_score': 0.07, 'max_score': 0.15, 'min_score': -0.04}
