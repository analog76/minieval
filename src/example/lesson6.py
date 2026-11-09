import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# 1. Load environment variables from .env file before initializing the client
load_dotenv()

# Verify the API key is present
if not os.getenv("OPENAI_API_KEY"):
    raise ValueError("OPENAI_API_KEY is missing. Check your .env file.")

# Initialize the OpenAI client (reads OPENAI_API_KEY from the loaded environment)
client = OpenAI()

# =====================================================================
# STAGE 1: The System Under Test (LLM 1 generates dynamic output)
# =====================================================================
def generate_agent_response(user_query: str) -> str:
    """This represents your actual AI product answering the user."""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.7,  # Allows natural conversational variation
        messages=[
            {
                "role": "system",
                "content": (
                    "You are a store support assistant. Rule: Items can only "
                    "be returned within 30 days of purchase for a full refund."
                ),
            },
            {"role": "user", "content": user_query},
        ],
    )
    return response.choices[0].message.content or ""


# =====================================================================
# STAGE 2: The Evaluators (LLM 2 acts as judge + rule checks)
# =====================================================================
def llm_judge_eval(user_query: str, live_output: str, expected_rule: str) -> dict:
    """Judge LLM evaluates the live response from the Agent LLM."""
    prompt = f"""
You are an objective grading judge.

User Question: {user_query}
Expected Rule: {expected_rule}
Actual Output: {live_output}

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
        messages=[{"role": "user", "content": prompt}],
    )

    data = json.loads(response.choices[0].message.content)
    grade = data.get("grade", "C").upper()
    grade_map = {"A": 1.0, "B": 0.5, "C": 0.0}

    return {
        "score": grade_map.get(grade, 0.0),
        "grade": grade,
        "reason": data.get("explanation", ""),
    }


def length_eval(live_output: str, max_words: int = 30) -> dict:
    """Deterministic check on word count."""
    count = len(live_output.split())
    passed = count <= max_words
    return {
        "score": 1.0 if passed else 0.0,
        "reason": f"{count}/{max_words} words.",
    }


# =====================================================================
# PIPELINE EXECUTION
# =====================================================================
if __name__ == "__main__":
    query = "Can I get a refund if I bought something two weeks ago?"
    rule = "Customers can return items within 30 days of purchase for a full refund."

    print(f"User Query: {query}\n" + "-" * 60)

    # 1. LIVE INFERENCE: Generate live response using LLM 1
    print("Step 1: Invoking Agent LLM to generate response...")
    live_response = generate_agent_response(query)
    print(f"Agent Live Response:\n\"{live_response}\"\n" + "-" * 60)

    # 2. EVALUATION: Score the live response
    print("Step 2: Evaluating the live response...")
    accuracy = llm_judge_eval(query, live_response, rule)
    length = length_eval(live_response, max_words=35)
    composite = (accuracy["score"] + length["score"]) / 2.0

    # 3. SCORECARD
    print(f"\nFinal Composite Score: {composite:.2f} / 1.0")
    print(f"* Accuracy Judge: {accuracy['score']} (Grade {accuracy['grade']}) -> {accuracy['reason']}")
    print(f"* Length Check:   {length['score']} -> {length['reason']}")