import asyncio
from dotenv import load_dotenv
from src.loader import load_dataset
from src.runner import EvalRunner
from src.scorers import citation_regex_scorer, llm_categorical_judge
from src.tasks import support_agent_task

load_dotenv()

async def run_suite():
    # 1. Load Data
    dataset = load_dataset("data/test_cases.jsonl")
    print(f"Loaded {len(dataset)} evaluation cases.\n" + "=" * 70)

    # 2. Assemble Pipeline
    runner = EvalRunner(
        task=support_agent_task,
        scorers=[citation_regex_scorer, llm_categorical_judge],
    )

    # 3. Execute
    results = await runner.run(dataset)

    # 4. Display Report
    total_score = 0.0
    for res in results:
        total_score += res["composite_score"]
        print(f"[{res['id']}] Query: {res['query']}")
        print(f"Output: {res['output']}")
        print(f"Composite Score: {res['composite_score']} / 1.0")
        for m_name, m_val in res["metrics"].items():
            print(f"  * {m_name}: {m_val['score']} -> {m_val['rationale']}")
        print("-" * 70)

    avg_score = total_score / len(results) if results else 0.0
    print(f"\nFinal Suite Average: {avg_score:.2f} / 1.0")

    # CI/CD Gate
    assert avg_score >= 0.60, f"Regression detected! Suite average {avg_score:.2f} < 0.60"

if __name__ == "__main__":
    asyncio.run(run_suite())