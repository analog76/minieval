import json
from pathlib import Path
from typing import List
from src.types import EvalCase

def load_dataset(file_path: str) -> List[EvalCase]:
    """Reads a JSONL file and yields typed EvalCase objects."""
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"Evaluation dataset missing at: {path.resolve()}")

    dataset: List[EvalCase] = []
    with open(path, "r", encoding="utf-8") as f:
        for line_num, line in enumerate(f, start=1):
            line_str = line.strip()
            if not line_str:
                continue
            try:
                record = json.loads(line_str)
                dataset.append(
                    EvalCase(
                        id=record.get("id", f"LINE-{line_num}"),
                        input=record["input"],
                        expected=record.get("expected"),
                        metadata=record.get("metadata", {}),
                    )
                )
            except (json.JSONDecodeError, KeyError) as e:
                raise ValueError(f"Malformed JSONL at line {line_num}: {e}")
    return dataset