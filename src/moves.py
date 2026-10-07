from __future__ import annotations

import random
from typing import List, Optional, Tuple

from src.model.package import Package
from src.model.state import State

Position = Tuple[int, int, int]

ROTATION_AXES: Tuple[str, ...] = ("x", "y", "z")


#move
def relocate(state: State, pkg_id: str, position: Optional[Position]) -> State:
    new = state.copy()
    new.set_position(pkg_id, position)
    return new


def swap(state: State, id_a: str, id_b: str) -> State:
    if id_a == id_b:
        return state.copy()
    new = state.copy()
    pos_a = new.placements[id_a]
    pos_b = new.placements[id_b]
    new.set_position(id_a, pos_b)
    new.set_position(id_b, pos_a)
    return new


def rotate_90(state: State, pkg_id: str, axis: str) -> State:
    if axis not in ROTATION_AXES:
        raise ValueError(f"rotate_90: sumbu harus x/y/z, dapat {axis!r}")
    new = state.copy()
    pkg = new.package_by_id(pkg_id)
    pkg.rotate(axis)
    return new


def candidate_positions(
    state: State,
    pkg_id: str,
    rng: random.Random,
    n: int = 20,
    grid_step: int = 1,
) -> List[Position]:
    truck = state.truck
    pkg = state.package_by_id(pkg_id)
    wd, ld, hd = pkg.oriented_dims
    tw, tl, th = truck.dim["w"], truck.dim["l"], truck.dim["h"]

    candidates: List[Position] = []

    # lantai z=0
    for x in range(0, max(1, tw - wd + 1), grid_step):
        for y in range(0, max(1, tl - ld + 1), grid_step):
            candidates.append((x, y, 0))

    for other in state.placed_packages():
        if other.id == pkg_id:
            continue
        assert other.position is not None
        ox, oy, oz = other.position
        ow, ol, oh = other.oriented_dims
        top_z = oz + oh
        if top_z + hd > th:
            continue  # tidak muat vertikal
        x_min = max(0, ox - wd + 1)
        x_max = min(tw - wd, ox + ow - 1)
        y_min = max(0, oy - ld + 1)
        y_max = min(tl - ld, oy + ol - 1)
        if x_min > x_max or y_min > y_max:
            continue
        for x in range(x_min, x_max + 1, grid_step):
            for y in range(y_min, y_max + 1, grid_step):
                candidates.append((x, y, top_z))

    for cx in (0, max(0, tw - wd)):
        for cy in (0, max(0, tl - ld)):
            pos = (cx, cy, 0)
            if pos not in candidates:
                candidates.append(pos)

    rng.shuffle(candidates)
    return candidates[:n]


def neighbor_states(
    state: State,
    rng: random.Random,
    n_neighbors: int = 60,
    grid_step: int = 1,
    use_swap: bool = True,
    use_relocate: bool = True,
    use_rotate: bool = True,
    filter_feasible: bool = True,
) -> List[State]:
    all_ids = [p.id for p in state.packages]
    if not all_ids:
        return []

    move_pool: List[str] = []
    if use_swap:
        move_pool.append("swap")
    if use_relocate:
        move_pool.append("relocate")
    if use_rotate:
        move_pool.append("rotate")
    if not move_pool:
        return []

    neighbors: List[State] = []
    seen_positions: set = set()
    attempts = 0
    max_attempts = n_neighbors * 10

    def _pos_key(s: State) -> tuple:
        return tuple(sorted((pid, pos) for pid, pos in s.placements.items()))

    while len(neighbors) < n_neighbors and attempts < max_attempts:
        attempts += 1
        move_type = rng.choice(move_pool)

        if move_type == "swap" and len(all_ids) >= 2:
            id_a, id_b = rng.sample(all_ids, 2)
            cand = swap(state, id_a, id_b)

        elif move_type == "relocate":
            pkg = rng.choice(state.packages)
            current_pos = state.placements[pkg.id]
            if current_pos is None:
                # paket di luar: muatkan ke dalam truk
                positions = candidate_positions(state, pkg.id, rng, n=10, grid_step=grid_step)
                if not positions:
                    continue
                cand = relocate(state, pkg.id, rng.choice(positions))
            else:
                # pindah ke posisi baru, atau keluarkan dari truk
                if rng.random() < 0.3:
                    cand = relocate(state, pkg.id, None)
                else:
                    positions = candidate_positions(state, pkg.id, rng, n=10, grid_step=grid_step)
                    if not positions:
                        continue
                    cand = relocate(state, pkg.id, rng.choice(positions))

        elif move_type == "rotate":
            pkg = rng.choice(state.packages)
            cand = rotate_90(state, pkg.id, rng.choice(ROTATION_AXES))
        else:
            continue

        key = _pos_key(cand)
        if key in seen_positions:
            continue

        if filter_feasible and not cand.is_feasible():
            continue

        seen_positions.add(key)
        neighbors.append(cand)

    return neighbors