## Upgrade to an LLM-as-a-Judge (Semantic Evaluation)

import json
from openai import OpenAI

client = OpenAI()

def llm_judge_eval(user_query: str, llm_output: str, expected_rule: str) -> dict:
    prompt = f"""
You are an objective grading judge.

User Question: {user_query}
Expected Rule: {expected_rule}
 

Select one category:
- Grade A: Output directly follows the rule and answers clearly.
- Grade B: Output is partially correct or contains unnecessary fluff.
- Grade C: Output is wrong, misses the rule, or hallucinates.

Respond ONLY with valid JSON:
{{
    "grade": "A" or "B" or "C",
    "explanation": "<short reason>"
}}
"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[{"role": "user", "content": prompt}]
    )

    # Parse judge's response
    result = json.loads(response.choices[0].message.content)
    grade = result.get("grade", "C")
    explanation = result.get("explanation", "")

    # Convert letter grades to normalized numbers (0.0 to 1.0)
    grade_to_score = {
        "A": 1.0,
        "B": 0.5,
        "C": 0.0
    }
    
    score = grade_to_score.get(grade, 0.0)

    return {
        "score": score,
        "grade": grade,
        "reason": explanation
    }

# =====================================================================
# 3. HOW TO INVOKE IT
# =====================================================================

# Test Case 1: Evaluating a good response
query = "How long do I have to return an item?"
rule = "Customers can return items within 30 days of purchase for a full refund."
good_response = "You have 30 days from the purchase date to return any item for a full refund."

result_1 = llm_judge_eval(
    user_query=query,
    llm_output=good_response,
    expected_rule=rule
)

print("Test 1 Evaluation Result:")
print(f"Score: {result_1['score']} (Grade: {result_1['grade']})")
print(f"Reason: {result_1['reason']}\n")


# Test Case 2: Evaluating a hallucinated / incorrect response
bad_response = "You can return items anytime within 1 year as long as you have the original box."

result_2 = llm_judge_eval(
    user_query=query,
    llm_output=bad_response,
    expected_rule=rule
)

print("Test 2 Evaluation Result:")
print(f"Score: {result_2['score']} (Grade: {result_2['grade']})")
print(f"Reason: {result_2['reason']}")