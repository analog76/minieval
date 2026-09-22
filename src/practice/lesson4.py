##Input Query ───> [ LLM Generates Output ] ───> [ Eval Function ] ───> Score (0.0 to 1.0)
##                                                        ▲
##                                                        │
##                                                Expected Criteria def check_return_window_eval(llm_output: str) -> dict:
 

def check_return_window_eval(llm_output: str) -> dict:
    # Look for the required phrase
    if "30 days" in llm_output.lower():
        return {
            "score": 1.0,
            "passed": True,
            "reason": "The output explicitly mentions the 30-day window."
        }
    else:
        return {
            "score": 0.0,
            "passed": False,
            "reason": "The output missed the required '30 days' timeframe."
        }

# --- Let's test it ---
test_output_good = "You can return your item within 30 days of purchase for a full refund."
test_output_bad = "You can return items anytime you want as long as you have the receipt."

print(check_return_window_eval(test_output_good))
# Output: {'score': 1.0, 'passed': True, 'reason': '...'}

print(check_return_window_eval(test_output_bad))
# Output: {'score': 0.0, 'passed': False, 'reason': '...'}