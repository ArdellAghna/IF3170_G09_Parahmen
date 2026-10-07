from __future__ import annotations

from src.constraints import check_feasible
from src.model.state import State


def objective(state: State) -> float:
    # total nilai paket di dalam truk
    feasible, violations = check_feasible(state)
    return state.total_value() if feasible else -float(len(violations))


def feasible_value(state: State) -> float:
    # Buat ngetest value yang feassible
    return state.total_value()