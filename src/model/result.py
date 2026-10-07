from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

from src.model.state import State


@dataclass
class Result:
    algorithm: str
    variant: Optional[str] = None
    params: Dict[str, Any] = field(default_factory=dict)
    seed: Optional[int] = None
    initial_state: Optional[State] = None
    final_state: Optional[State] = None
    initial_objective: float = 0.0
    final_objective: float = 0.0
    history: List[float] = field(default_factory=list)
    duration: float = 0.0
    n_iterations: int = 0
    metrics: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "algorithm": self.algorithm,
            "variant": self.variant,
            "params": dict(self.params),
            "seed": self.seed,
            "initial_objective": self.initial_objective,
            "final_objective": self.final_objective,
            "history": list(self.history),
            "duration": self.duration,
            "n_iterations": self.n_iterations,
            "metrics": dict(self.metrics),
            "initial_state": None if self.initial_state is None else self.initial_state.to_dict(),
            "final_state": None if self.final_state is None else self.final_state.to_dict(),
        }


class Stopwatch:

    def __enter__(self) -> "Stopwatch":
        self.start = time.perf_counter()
        return self

    def __exit__(self, *exc) -> None:
        self.elapsed = time.perf_counter() - self.start