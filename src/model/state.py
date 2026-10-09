from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, List, Optional, Tuple

from src.model.package import Package
from src.model.truck import Truck

Position = Tuple[int, int, int]

class State:
    # penempatan: Kalo none diluar treuk
    def __init__(self, truck: Truck, packages: List[Package]) -> None:
        self.truck = truck
        self.packages: List[Package] = list(packages)

        self.placements: Dict[str, Optional[Position]] = {
            pkg.id: (None if pkg.position is None else tuple(pkg.position))
            for pkg in self.packages
        }
        for pkg in self.packages:
            pkg.position = self.placements[pkg.id]

    #akses
    def package_by_id(self, pkg_id: str) -> Package:
        for pkg in self.packages:
            if pkg.id == pkg_id:
                return pkg
        raise KeyError(f"State.package_by_id: id paket tidak dikenal {pkg_id!r}")

    def placed_packages(self) -> List[Package]:
        return [p for p in self.packages if self.placements.get(p.id) is not None]

    def outside_packages(self) -> List[Package]:
        return [p for p in self.packages if self.placements.get(p.id) is None]

    def total_value(self) -> float:
        return float(sum(p.val for p in self.placed_packages()))

    def total_weight(self) -> float:
        return float(sum(p.w for p in self.placed_packages()))

    def value(self) -> float:
        return self.total_value()

    def is_feasible(self) -> bool:
        from src.constraints import check_feasible  # impor lokal: hindari lingkaran

        return check_feasible(self)[0]

    def set_position(self, pkg_id: str, position: Optional[Position]) -> None:
        if pkg_id not in self.placements:
            raise KeyError(f"State.set_position: id paket tidak dikenal {pkg_id!r}")
        if position is not None:
            position = tuple(int(c) for c in position)  # type: ignore[assignment]
        self.placements[pkg_id] = position  # type: ignore[assignment]
        self.package_by_id(pkg_id).position = self.placements[pkg_id]

    #salinan
    def copy(self) -> "State":
        return deepcopy(self)

    #JSON
    def to_dict(self) -> Dict[str, Any]:
        return {
            "truck": self.truck.to_dict(),
            "placements": {
                pid: (None if pos is None else list(pos))
                for pid, pos in self.placements.items()
            },
            "packages": [p.to_dict() for p in self.packages],
            "value": self.total_value(),
            "weight": self.total_weight(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "State":
        truck = Truck.from_dict(data["truck"])
        packages = [Package.from_dict(p) for p in data["packages"]]
        state = cls(truck, packages)
        for pid, pos in data["placements"].items():
            state.set_position(pid, None if pos is None else tuple(pos))
        return state

    def summary(self) -> str:
        return (
            f"State({self.truck}, value={self.total_value():.2f}, "
            f"weight={self.total_weight():.2f}/{self.truck.max_cap}, "
            f"inside={len(self.placed_packages())}/{len(self.packages)})"
        )

    def __repr__(self) -> str:
        return self.summary()