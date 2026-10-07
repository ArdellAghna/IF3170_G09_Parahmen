from __future__ import annotations

from typing import Dict, Optional

from src.model.package import Package
from src.model.state import State
from src.model.truck import Truck


def make_package(
    pkg_id: str,
    w: int = 2,
    l: int = 2,
    h: int = 2,
    value: float = 10,
    weight: float = 1,
    is_fragile: bool = False,
    eta: int = 1,
    position=None,
    orientation: Optional[Dict[str, str]] = None,
) -> Package:
    return Package(
        pkg_id,
        dim={"w": w, "l": l, "h": h},
        val=value,
        w=weight,
        is_fragile=is_fragile,
        eta=eta,
        position=position,
        orientation=orientation,
    )


def make_state(truck, packages):
    return State(truck, list(packages))


def make_truck(w=10, l=10, h=10, max_cap=100):
    return Truck(dim={"w": w, "l": l, "h": h}, max_cap=max_cap)
