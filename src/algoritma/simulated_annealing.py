from __future__ import annotations

import math
import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from src.model.result import Result
from src.model.state import State
from src.moves import neighbor_states
from src.objective import objective
from src.utilitas.helpers import _now, asdict_safe

# Parameter SA
@dataclass
class SAParams:
    max_iterations: int = 1000
    n_neighbors: int = 1
    grid_step: int = 1
    temp_initial: float = 100.0
    temp_min: float = 0.01
    cooling_rate: float = 0.995
    schedule: str = "exponential"
    max_no_neighbor_retries: int = 100

def run(
    initial_state: State,
    params: Optional[SAParams] = None,
    seed: int = 0,
) -> Result:
    params = params or SAParams()

    rng = random.Random(seed)
    start_time = _now()

    initial_obj = objective(initial_state)
    history: List[float] = [initial_obj]
    metrics: Dict[str, Any] = {
        "schedule": params.schedule,
        "accepted_equal": 0,
        "accepted_worse": 0,
        "rejected": 0,
        "improving_moves": 0,
        "stuck_count": 0,
        "no_neighbor_steps": 0,
        "final_temp": params.temp_initial,
    }

    prob_history: List[float] = []
    current_history: List[float] = [initial_obj]
    current = initial_state.copy()
    current_obj = initial_obj
    best_state = current.copy()
    best_obj = current_obj

    T = params.temp_initial
    n_iter = 0
    empty_streak = 0
    while n_iter < params.max_iterations:
        if T < params.temp_min:
            break

        neighbors = neighbor_states(current, rng, n_neighbors = params.n_neighbors, grid_step = params.grid_step)
        if not neighbors:
            metrics["no_neighbor_steps"] += 1
            empty_streak += 1
            if empty_streak >= params.max_no_neighbor_retries:
                break
            continue
        empty_streak = 0

        best_neighbor_obj = max(objective(nb) for nb in neighbors)
        if best_neighbor_obj <= current_obj:
            metrics["stuck_count"] += 1

        next_state = rng.choice(neighbors)
        next_obj = objective(next_state)
        delta_e = next_obj - current_obj
        try:
            exp_val = math.exp(delta_e / T)
        except OverflowError:
            exp_val = float("inf")

        prob_history.append(exp_val)

        if delta_e > 0:
            current = next_state.copy()
            current_obj = next_obj
            metrics["improving_moves"] += 1
        elif delta_e == 0:
            current = next_state.copy()
            current_obj = next_obj
            metrics["accepted_equal"] += 1
        else:
            if rng.random() < exp_val:
                current = next_state.copy()
                current_obj = next_obj
                metrics["accepted_worse"] += 1
            else:
                metrics["rejected"] += 1
        if current_obj > best_obj:
            best_obj = current_obj
            best_state = current.copy()
        if params.schedule == "exponential":
            T *= params.cooling_rate
        else:
            T = params.temp_initial * (1.0 - (n_iter + 1) / params.max_iterations)
        n_iter += 1
        history.append(best_obj)
        current_history.append(current_obj)

    metrics["final_temp"] = T
    metrics["prob_history"] = prob_history
    metrics["current_history"] = current_history
    duration = _now() - start_time

    return Result(
        algorithm="simulated_annealing",
        variant=params.schedule,
        params=asdict_safe(params),
        seed=seed,
        initial_state=initial_state,
        final_state=best_state,
        initial_objective=initial_obj,
        final_objective=best_obj,
        history=history,
        duration=duration,
        n_iterations=n_iter,
        metrics=metrics,
    )