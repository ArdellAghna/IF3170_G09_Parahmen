from __future__ import annotations

import random
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from src.model.result import Result
from src.model.state import State
from src.moves import neighbor_states
from src.objective import objective
from src.utilitas.helpers import _now, asdict_safe

# Varian HC
VARIANTS: Tuple[str, ...] = ("steepest", "sideways", "restart", "stochastic")

# Parameter HC
@dataclass
class HCParams:
    variant: str = "steepest"
    max_iterations: int = 200
    n_neighbors: int = 60
    grid_step: int = 1
    max_sideways: int = 30
    sideways_prob: float = 0.1
    max_restart: int = 5
    iterations_per_restart: int = 100
    no_improvement_limit: Optional[int] = None


def run(
    initial_state: State,
    params: Optional[HCParams] = None,
    seed: int = 0,
) -> Result:
    params = params or HCParams()
    if params.variant not in VARIANTS:
        raise ValueError(f"hill_climbing.run: variant tidak dikenal {params.variant!r}")

    rng = random.Random(seed)
    start_time = _now()

    initial_obj = objective(initial_state)
    history: List[float] = [initial_obj]
    metrics: Dict[str, Any] = {
        "variant": params.variant,
        "sideways_moves": 0,
        "restarts": 0,
        "iterations_per_restart": [],
        "improving_moves": 0,
    }

    best_state = initial_state.copy()
    best_obj = initial_obj

    if params.variant == "restart":
        total_iters = 0
        n_restarts = 0
        for r in range(params.max_restart + 1):
            if r == 0:
                start_state = initial_state.copy()
            else:
                start_state = _random_restart_state(initial_state, rng)
                n_restarts += 1
            seg_state, seg_obj, seg_hist, seg_iters, seg_side, seg_imp = _climb_segment(
                start_state, params, rng
            )
            metrics["iterations_per_restart"].append(seg_iters)
            metrics["sideways_moves"] += seg_side
            metrics["improving_moves"] += seg_imp
            total_iters += seg_iters
            history.extend(seg_hist if r > 0 else seg_hist[1:])
            if seg_obj > best_obj:
                best_obj, best_state = seg_obj, seg_state
            if n_restarts >= params.max_restart:
                break
        metrics["restarts"] = n_restarts
        final_state, n_iter = best_state, total_iters

    else:
        final_state, best_obj, seg_hist, n_iter, seg_side, seg_imp = _climb_segment(
            initial_state, params, rng
        )
        best_state = final_state
        history.extend(seg_hist[1:])
        metrics["sideways_moves"] += seg_side
        metrics["improving_moves"] += seg_imp

    duration = _now() - start_time

    return Result(
        algorithm="hill_climbing",
        variant=params.variant,
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

# Main Func
def _climb_segment(
    start_state: State,
    params: HCParams,
    rng: random.Random,
) -> Tuple[State, float, List[float], int, int, int]:
    current = start_state.copy()
    current_obj = objective(current)
    best_obj = current_obj
    history: List[float] = [current_obj]
    n_iter = 0
    sideways_used = 0
    sideways_count = 0
    improving_count = 0
    since_improve = 0
    n_neighbors = params.n_neighbors

    while n_iter < params.max_iterations:
        neighbors = neighbor_states(
            current,
            rng,
            n_neighbors=n_neighbors,
            grid_step=params.grid_step,
        )
        if not neighbors:
            break

        scored = [(objective(nb), nb) for nb in neighbors]
        n_iter += 1

        accepted = False
        sideways_now = False
        if params.variant == "stochastic":
            # Stochastic
            improving = [(o, nb) for o, nb in scored if o > current_obj]
            if improving:
                choice = rng.choice(improving)
                current, current_obj = choice[1].copy(), choice[0]
                accepted = True
            elif rng.random() < params.sideways_prob:
                # sideways acak
                equal = [(o, nb) for o, nb in scored if o == current_obj]
                if equal:
                    choice = rng.choice(equal)
                    current, current_obj = choice[1].copy(), choice[0]
                    accepted = True
                    sideways_now = True
        else:
            # Steepest & sideways & restart
            best_neighbor_obj, best_neighbor = max(scored, key=lambda t: t[0])
            if best_neighbor_obj > current_obj:
                current, current_obj = best_neighbor.copy(), best_neighbor_obj
                accepted = True
            elif (
                params.variant in ("sideways", "restart")
                and best_neighbor_obj == current_obj
                and sideways_used < params.max_sideways
            ):
                current, current_obj = best_neighbor.copy(), best_neighbor_obj
                sideways_used += 1
                accepted = True
                sideways_now = True

        if sideways_now:
            sideways_count += 1
        if current_obj > best_obj:
            improving_count += 1
            best_obj = current_obj
            since_improve = 0
        elif not accepted:
            since_improve += 1

        history.append(best_obj)

        if params.no_improvement_limit and since_improve >= params.no_improvement_limit:
            break

    return current, best_obj, history, n_iter, sideways_count, improving_count


def _random_restart_state(basis: State, rng: random.Random) -> State:
    from src.init import random_initial_state

    return random_initial_state(basis.truck, basis.packages, rng)