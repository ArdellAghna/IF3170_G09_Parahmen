from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

from src.model.result import Result
from src.model.state import State
from src.moves import neighbor_states
from src.objective import objective
from src.utilitas.helpers import _now, asdict_safe

# Parameter GA
@dataclass
class GAParams:
    pop_size: int = 20
    max_generations: int = 100
    mutation_rate: float = 0.1
    n_neighbors: int = 15
    grid_step: int = 1
    elitism: int = 2
    no_improvement_limit: Optional[int] = None

def run(
    initial_state: State,
    params: Optional[GAParams] = None,
    seed: int = 0,
) -> Result:
    params = params or GAParams()
    rng = random.Random(seed)
    start_time = _now()
    population = _init_population(initial_state, params.pop_size, rng)
    scored = [(objective(ind), ind) for ind in population]

    gen_best_obj = max(s for s, _ in scored)
    gen_avg_obj = sum(s for s, _ in scored) / len(scored)
    
    history: List[float] = [gen_best_obj]
    avg_history: List[float] = [gen_avg_obj]
    metrics: Dict[str, Any] = {
        "crossovers": 0,
        "mutations": 0,
        "improving_generations": 0,
    }

    best_obj, best_state = max(scored, key=lambda t: t[0])
    since_improve = 0
    n_gen = 0

    while n_gen < params.max_generations:
        new_population: List[State] = []
        sorted_pop = sorted(scored, key=lambda t: t[0], reverse=True)
        for _, elite in sorted_pop[: params.elitism]:
            new_population.append(elite.copy())
        while len(new_population) < params.pop_size:
            parent_a = _roulette_selection(scored, rng)
            parent_b = _roulette_selection(scored, rng)
            child = _crossover(parent_a, parent_b, rng)
            metrics["crossovers"] += 1
            if rng.random() < params.mutation_rate:
                child = _mutate(child, rng, params)
                metrics["mutations"] += 1
            new_population.append(child)
        population = new_population
        scored = [(objective(ind), ind) for ind in population]
        gen_best_obj, gen_best_state = max(scored, key=lambda t: t[0])
        gen_avg_obj = sum(s for s, _ in scored) / len(scored)
        n_gen += 1
        if gen_best_obj > best_obj:
            best_obj = gen_best_obj
            best_state = gen_best_state.copy()
            since_improve = 0
            metrics["improving_generations"] += 1
        else:
            since_improve += 1
        history.append(gen_best_obj)
        avg_history.append(gen_avg_obj)
        if params.no_improvement_limit and since_improve >= params.no_improvement_limit:
            break

    duration = _now() - start_time
    initial_state_copy = initial_state.copy()
    initial_obj_real = objective(initial_state_copy)
    metrics["avg_history"] = avg_history

    return Result(
        algorithm="genetic_algorithm",
        variant=None,
        params=asdict_safe(params),
        seed=seed,
        initial_state=initial_state,
        final_state=best_state,
        initial_objective=initial_obj_real,
        final_objective=best_obj,
        history=history,
        duration=duration,
        n_iterations=n_gen,
        metrics=metrics,
    )

# Helper
def _init_population(basis: State, pop_size: int, rng: random.Random) -> List[State]:
    from src.init import random_initial_state
    population = [basis.copy()]
    for i in range(pop_size - 1):
        individual = random_initial_state(basis.truck, basis.packages, rng)
        population.append(individual)
    return population

def _roulette_selection(scored: List[Tuple[float, State]], rng: random.Random) -> State:
    scores = [s for s, _ in scored]
    min_score = min(scores)
    if min_score <= 0:
        shift = abs(min_score) + 1.0
    else:
        shift = 0.0
    weights = [s + shift for s in scores]
    total = sum(weights)
    if total == 0:
        return rng.choice([ind for _, ind in scored]).copy()
    pick = rng.uniform(0, total)
    cumulative = 0.0
    for weight, (_, ind) in zip(weights, scored):
        cumulative += weight
        if cumulative >= pick:
            return ind.copy()
    return scored[-1][1].copy()

def _crossover(parent_a: State, parent_b: State, rng: random.Random) -> State:
    from src.constraints import check_feasible
    
    all_ids = [p.id for p in parent_a.packages]
    if len(all_ids) < 2:
        return parent_a.copy()

    cut = rng.randint(1, len(all_ids) - 1)
    child = parent_a.copy()

    for pkg_id in all_ids[cut:]:
        pkg_b = parent_b.package_by_id(pkg_id)
        child_pkg = child.package_by_id(pkg_id)
        orig_orient = dict(child_pkg.orient)
        orig_pos = child.placements.get(pkg_id)
        child_pkg.set_orientation(dict(pkg_b.orient))
        child.set_position(pkg_id, parent_b.placements.get(pkg_id))
        feasible, _ = check_feasible(child)
        if not feasible:
            child_pkg.set_orientation(orig_orient)
            child.set_position(pkg_id, orig_pos)

    feasible, _ = check_feasible(child)
    if not feasible:
        return parent_a.copy()
    return child

def _mutate(state: State, rng: random.Random, params: GAParams) -> State:
    neighbors = neighbor_states(state, rng, n_neighbors = params.n_neighbors, grid_step = params.grid_step)
    if not neighbors:
        return state
    return rng.choice(neighbors)