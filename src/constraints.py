from __future__ import annotations

from typing import Dict, List, Tuple

from src.model.package import Package
from src.model.state import State

Position = Tuple[int, int, int]


#primitif
def _dims_xyz(pkg: Package) -> Tuple[int, int, int]:
    return pkg.oriented_dims


def _xyz_position(pkg: Package) -> Position:
    assert pkg.position is not None, "paket di luar truk tidak punya posisi"
    return pkg.position


def _rect_overlap(
    a_min: int, a_max: int, b_min: int, b_max: int
) -> bool:
    return a_min < b_max and b_min < a_max


def boxes_overlap(a: Package, b: Package) -> bool:
    if a.position is None or b.position is None:
        return False
    ax, ay, az = a.position
    bx, by, bz = b.position
    aw, al, ah = _dims_xyz(a)
    bw, bl, bh = _dims_xyz(b)
    return (
        _rect_overlap(ax, ax + aw, bx, bx + bw)
        and _rect_overlap(ay, ay + al, by, by + bl)
        and _rect_overlap(az, az + ah, bz, bz + bh)
    )


def _footprints_overlap(a: Package, b: Package) -> bool:
    if a.position is None or b.position is None:
        return False
    ax, ay, _ = a.position
    bx, by, _ = b.position
    aw, al, _ = _dims_xyz(a)
    bw, bl, _ = _dims_xyz(b)
    return _rect_overlap(ax, ax + aw, bx, bx + bw) and _rect_overlap(ay, ay + al, by, by + bl)


def in_bounds(pkg: Package, truck) -> bool:
    if pkg.position is None:
        return True 
    x, y, z = pkg.position
    w, l, h = _dims_xyz(pkg)
    tw, tl, th = truck.dim["w"], truck.dim["l"], truck.dim["h"]
    return x >= 0 and y >= 0 and z >= 0 and x + w <= tw and y + l <= tl and z + h <= th


def supporting_packages(pkg: Package, others: List[Package]) -> List[Package]:
    if pkg.position is None:
        return []
    _, _, zi = pkg.position
    supports: List[Package] = []
    for j in others:
        if j.id == pkg.id or j.position is None:
            continue
        _, _, zj = j.position
        _, _, hj = _dims_xyz(j)
        if zj + hj == zi and _footprints_overlap(j, pkg):
            supports.append(j)
    return supports


def has_support(pkg: Package, others: List[Package], truck) -> bool:
    if pkg.position is None:
        return True
    _, _, zi = pkg.position
    if zi == 0:
        return True
    return len(supporting_packages(pkg, others)) > 0


def supported_packages(pkg: Package, others: List[Package]) -> List[Package]:
    if pkg.position is None:
        return []
    _, _, zi = pkg.position
    _, _, hi = _dims_xyz(pkg)
    above: List[Package] = []
    for j in others:
        if j.id == pkg.id or j.position is None:
            continue
        _, _, zj = j.position
        if zj == zi + hi and _footprints_overlap(pkg, j):
            above.append(j)
    return above


def fragile_supports(fragile: Package, others: List[Package]) -> List[Package]:
    return supported_packages(fragile, others)


def capacity_ok(state: State) -> bool:
    return state.total_weight() <= state.truck.max_cap


def overlap_pairs(state: State) -> List[Tuple[str, str]]:
    inside = state.placed_packages()
    pairs: List[Tuple[str, str]] = []
    for i, a in enumerate(inside):
        for b in inside[i + 1 :]:
            if boxes_overlap(a, b):
                pairs.append((a.id, b.id))
    return pairs


def check_feasible(state: State) -> Tuple[bool, List[str]]:
    violations: List[str] = []
    truck = state.truck
    inside = state.placed_packages()

    for pkg in inside:
        if not in_bounds(pkg, truck):
            violations.append(f"C1_bounds:{pkg.id}")

    for a_id, b_id in overlap_pairs(state):
        violations.append(f"C5_overlap:{a_id}|{b_id}")

    for pkg in inside:
        if not has_support(pkg, inside, truck):
            violations.append(f"C2_floating:{pkg.id}")

    for pkg in inside:
        if pkg.is_fragile:
            for upper in fragile_supports(pkg, inside):
                violations.append(f"C3_fragile:{pkg.id}>{upper.id}")

    if not capacity_ok(state):
        violations.append("C4_capacity")

    return (len(violations) == 0), violations