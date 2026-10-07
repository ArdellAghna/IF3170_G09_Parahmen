from __future__ import annotations

import random
from typing import List, Optional, Tuple

from src.constraints import check_feasible
from src.model.package import Package
from src.model.state import State
from src.model.truck import Truck
from src.moves import candidate_positions

Position = Tuple[int, int, int]


def random_initial_state(
    truck: Truck,
    packages: List[Package],
    rng: random.Random,
    grid_step: int = 1,
    n_candidates: int = 12,
) -> State:
    state = State(truck, packages)
    state.packages = [p.copy() for p in packages]
    state.placements = {p.id: None for p in state.packages}
    for p in state.packages:
        p.position = None

    order = list(state.packages)
    rng.shuffle(order)

    for pkg in order:
        orientations = [dict(pkg.orient)]
        for _ in range(2):
            axis = rng.choice(("x", "y", "z"))
            trial = pkg.copy()
            trial.rotate(axis)
            orientations = orientations + [dict(trial.orient)]

        placed = False
        for orient in orientations:
            if placed:
                break
            pkg.set_orientation(orient)
            positions = candidate_positions(state, pkg.id, rng, n=n_candidates, grid_step=grid_step)
            rng.shuffle(positions)
            for pos in positions:
                state.set_position(pkg.id, pos)
                feasible, _ = check_feasible(state)
                if feasible:
                    placed = True
                    break
                state.set_position(pkg.id, None)  # rollback

        if not placed:
            state.set_position(pkg.id, None)

    return state