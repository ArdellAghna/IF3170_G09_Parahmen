from __future__ import annotations
from src.init import random_initial_state


import random
from dataclasses import dataclass, replace
from typing import Any, Dict, List, Optional, Tuple

from src.model.result import Result
from src.model.state import State
from src.moves import neighbor_states
from src.objective import objective
from src.utilitas.helpers import _now, asdict_safe

# Varian HC
VARIANTS: Tuple[str, ...] = ("steepest", "sideways", "restart", "stochastic")

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


ClimbOutcome = Tuple[State, float, List[float], int, int, int]

# Helper
def _score_neighbors(
    state: State,
    params: HCParams,
    rng: random.Random,
) -> List[Tuple[float, State]]:
    neighbors = neighbor_states(
        state,
        rng,
        n_neighbors=params.n_neighbors,
        grid_step=params.grid_step,
    )
    return [(objective(nb), nb) for nb in neighbors]


def _random_restart_state(basis: State, rng: random.Random) -> State:
    return random_initial_state(basis.truck, basis.packages, rng)



def _steepest_ascent(
    start_state: State,
    params: HCParams,
    rng: random.Random,
) -> ClimbOutcome:
    current = start_state.copy()
    current_obj = objective(current)
    best_obj = current_obj
    history: List[float] = [current_obj]
    n_iter = 0
    improving_count = 0
    since_improve = 0

    while n_iter < params.max_iterations:
        scored = _score_neighbors(current, params, rng)
        if not scored:
            break

        n_iter += 1
        best_neighbor_obj, best_neighbor = max(scored, key=lambda t: t[0])

        if best_neighbor_obj > current_obj:
            current, current_obj = best_neighbor.copy(), best_neighbor_obj
            best_obj = current_obj
            improving_count += 1
            since_improve = 0
            history.append(best_obj)
        else:
            since_improve += 1
            history.append(best_obj)
            break  # local optimum

        if params.no_improvement_limit and since_improve >= params.no_improvement_limit:
            break

    return current, best_obj, history, n_iter, 0, improving_count


def _sideways_move(
    start_state: State,
    params: HCParams,
    rng: random.Random,
) -> ClimbOutcome:
    current = start_state.copy()
    current_obj = objective(current)
    best_obj = current_obj
    history: List[float] = [current_obj]
    n_iter = 0
    sideways_used = 0
    sideways_count = 0
    improving_count = 0
    since_improve = 0

    while n_iter < params.max_iterations:
        scored = _score_neighbors(current, params, rng)
        if not scored:
            break

        n_iter += 1
        best_neighbor_obj, best_neighbor = max(scored, key=lambda t: t[0])

        accepted = False
        sideways_now = False

        if best_neighbor_obj > current_obj:
            current, current_obj = best_neighbor.copy(), best_neighbor_obj
            best_obj = current_obj
            improving_count += 1
            accepted = True
            since_improve = 0
        elif best_neighbor_obj == current_obj and sideways_used < params.max_sideways:
            current, current_obj = best_neighbor.copy(), best_neighbor_obj
            sideways_used += 1
            sideways_count += 1
            accepted = True
            sideways_now = True

        if not accepted:
            since_improve += 1

        history.append(best_obj)

        if sideways_now and sideways_used >= params.max_sideways:
            break

        if not accepted:
            break

        if params.no_improvement_limit and since_improve >= params.no_improvement_limit:
            break

    return current, best_obj, history, n_iter, sideways_count, improving_count


def _stochastic(
    start_state: State,
    params: HCParams,
    rng: random.Random,
) -> ClimbOutcome:
    current = start_state.copy()
    current_obj = objective(current)
    best_obj = current_obj
    history: List[float] = [current_obj]
    n_iter = 0
    sideways_count = 0
    improving_count = 0
    since_improve = 0

    while n_iter < params.max_iterations:
        scored = _score_neighbors(current, params, rng)
        if not scored:
            break

        n_iter += 1
        accepted = False
        sideways_now = False

        improving = [(o, nb) for o, nb in scored if o > current_obj]
        if improving:
            next_obj, next_state = rng.choice(improving)
            current, current_obj = next_state.copy(), next_obj
            accepted = True
        elif rng.random() < params.sideways_prob:
            equal = [(o, nb) for o, nb in scored if o == current_obj]
            if equal:
                next_obj, next_state = rng.choice(equal)
                current, current_obj = next_state.copy(), next_obj
                accepted = True
                sideways_now = True

        if sideways_now:
            sideways_count += 1

        if current_obj > best_obj:
            best_obj = current_obj
            improving_count += 1
            since_improve = 0
        elif not accepted:
            since_improve += 1

        history.append(best_obj)

        if not accepted:
            break  # tidak ada langkah yang diterima

        if params.no_improvement_limit and since_improve >= params.no_improvement_limit:
            break

    return current, best_obj, history, n_iter, sideways_count, improving_count


def _random_restart(
    initial_state: State,
    params: HCParams,
    rng: random.Random,
) -> Tuple[State, float, List[float], int, int, int, int, List[int]]:
    best_state = initial_state.copy()
    best_obj = objective(initial_state)
    history: List[float] = [best_obj]
    total_iters = 0
    n_restarts = 0
    sideways_total = 0
    improving_total = 0
    iterations_per_restart: List[int] = []

    for r in range(params.max_restart + 1):
        if r == 0:
            start_state = initial_state.copy()
        else:
            start_state = _random_restart_state(initial_state, rng)
            n_restarts += 1

        seg_params = (
            replace(params, max_iterations=params.iterations_per_restart)
            if params.iterations_per_restart > 0
            else params
        )
        seg_state, seg_obj, seg_hist, seg_iters, seg_side, seg_imp = _sideways_move(
            start_state, seg_params, rng
        )

        iterations_per_restart.append(seg_iters)
        sideways_total += seg_side
        improving_total += seg_imp
        total_iters += seg_iters
        history.extend(seg_hist if r > 0 else seg_hist[1:])

        if seg_obj > best_obj:
            best_obj, best_state = seg_obj, seg_state

        if n_restarts >= params.max_restart:
            break

    return (
        best_state,
        best_obj,
        history,
        total_iters,
        sideways_total,
        improving_total,
        n_restarts,
        iterations_per_restart,
    )



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

    if params.variant == "restart":
        final_state, best_obj, history, n_iter, sideways, improving, restarts, ipr = _random_restart(
            initial_state, params, rng
        )
        metrics: Dict[str, Any] = {
            "variant": params.variant,
            "sideways_moves": sideways,
            "restarts": restarts,
            "iterations_per_restart": ipr,
            "improving_moves": improving,
        }
    else:
        climbers = {
            "steepest": _steepest_ascent,
            "sideways": _sideways_move,
            "stochastic": _stochastic,
        }
        final_state, best_obj, history, n_iter, sideways, improving = climbers[params.variant](
            initial_state, params, rng
        )
        metrics = {
            "variant": params.variant,
            "sideways_moves": sideways,
            "restarts": 0,
            "iterations_per_restart": [],
            "improving_moves": improving,
        }

    duration = _now() - start_time

    return Result(
        algorithm="hill_climbing",
        variant=params.variant,
        params=asdict_safe(params),
        seed=seed,
        initial_state=initial_state,
        final_state=final_state,
        initial_objective=initial_obj,
        final_objective=best_obj,
        history=history,
        duration=duration,
        n_iterations=n_iter,
        metrics=metrics,
    )
