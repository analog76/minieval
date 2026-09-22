import json
import re
from typing import Any, Dict, Optional
from openai import AsyncOpenAI
from src.types import ScoreResult

client = AsyncOpenAI()

async def citation_regex_scorer(
    input_data: Dict[str, Any], output: str, expected: Optional[str]
) -> ScoreResult:
    """Deterministic Scorer: Fast regex validation for policy codes."""
    pattern = r"\b[A-Z]{3}-\d{3}\b"
    match = re.search(pattern, output)
    score = 1.0 if bool(match) else 0.0
    rationale = f"Matched tag: '{match.group(0)}'" if match else "Missing policy citation code."
    return ScoreResult(name="citation_format", score=score, rationale=rationale)


async def llm_categorical_judge(
    input_data: Dict[str, Any], output: str, expected: Optional[str]
) -> ScoreResult:
    """LLM-as-a-Judge: Categorical rubric mapped to [0.0, 1.0]."""
    prompt = f"""
Evaluate the response against the user inquiry and the expected target.

User Query: {input_data.get("query")}
Expected Criteria: {expected}
Actual Output: {output}

Categorize the response into one of the following:
- Category A: Directly answers the user inquiry with accurate and actionable details.
- Category B: Partially answers the inquiry, or contains excessive conversational fluff/minor omissions.
- Category C: Completely deflects, hallucinates, or fails to address the question.

Respond in strict JSON:
{{
  "category": "A" | "B" | "C",
  "rationale": "<concise explanation>"
}}
"""
    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        temperature=0.0,
        response_format={"type": "json_object"},
        messages=[
            {"role": "system", "content": "You are an objective eval grading judge."},
            {"role": "user", "content": prompt},
        ],
    )

    data = json.loads(response.choices[0].message.content or "{}")
    cat = data.get("category", "C").upper()
    rationale = data.get("rationale", "No rationale returned")

    category_map = {"A": 1.0, "B": 0.5, "C": 0.0}
    return ScoreResult(
        name="answer_quality",
        score=category_map.get(cat, 0.0),
        rationale=f"[{cat}] {rationale}",
    )