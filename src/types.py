from dataclasses import dataclass, field
from typing import Any, Callable, Coroutine, Dict, Optional

@dataclass
class EvalCase:
    """Pillar 1: Data representation."""
    id: str
    input: Dict[str, Any]
    expected: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class ScoreResult:
    """Pillar 3: Normalized metric output."""
    name: str
    score: float  # Strictly normalized: 0.0 <= score <= 1.0
    rationale: str = ""

# Generic asynchronous callables
TaskFn = Callable[[Dict[str, Any]], Coroutine[Any, Any, str]]
ScorerFn = Callable[[Dict[str, Any], str, Optional[str]], Coroutine[Any, Any, ScoreResult]]