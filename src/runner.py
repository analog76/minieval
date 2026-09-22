import asyncio
from typing import Any, Dict, List
from src.types import EvalCase, ScorerFn, TaskFn

class EvalRunner:
    """Generic orchestrator running test cases against scoring rubrics."""

    def __init__(self, task: TaskFn, scorers: List[ScorerFn]):
        self.task = task
        self.scorers = scorers

    async def _evaluate_single_case(self, case: EvalCase) -> Dict[str, Any]:
        actual_output = await self.task(case.input)
        
        # Run all scorers concurrently for this test case
        score_tasks = [
            scorer(case.input, actual_output, case.expected)
            for scorer in self.scorers
        ]
        scores = await asyncio.gather(*score_tasks)

        composite = sum(s.score for s in scores) / len(scores) if scores else 0.0

        return {
            "id": case.id,
            "query": case.input.get("query"),
            "output": actual_output,
            "composite_score": round(composite, 2),
            "metrics": {s.name: {"score": s.score, "rationale": s.rationale} for s in scores},
        }

    async def run(self, dataset: List[EvalCase]) -> List[Dict[str, Any]]:
        # Execute all test cases concurrently
        tasks = [self._evaluate_single_case(case) for case in dataset]
        return await asyncio.gather(*tasks)