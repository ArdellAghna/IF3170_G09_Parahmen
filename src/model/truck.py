from __future__ import annotations

from copy import deepcopy
from typing import Any, Dict, Optional


class Truck:
    def __init__(
        self,
        dim: Optional[Dict[str, int]] = None,
        max_cap: float = 0,
        *,
        dimensions: Optional[Dict[str, int]] = None,
        max_capacity: Optional[float] = None,
    ) -> None:
        if dim is not None and dimensions is not None:
            raise ValueError("Truck: isi hanya salah satu dari dim/dimensions")
        if dim is None:
            dim = dimensions
        if dim is None:
            dim = {"w": 10, "l": 10, "h": 10}

        self.dim: Dict[str, int] = dict(dim)
        self.max_cap: float = max_capacity if max_capacity is not None else max_cap

    #properti
    @property
    def w(self) -> int:
        return self.dim["w"]

    @property
    def l(self) -> int:
        return self.dim["l"]

    @property
    def h(self) -> int:
        return self.dim["h"]

    def copy(self) -> "Truck":
        return deepcopy(self)

    #JSON
    def to_dict(self) -> Dict[str, Any]:
        return {
            "dimensions": dict(self.dim),
            "max_capacity": self.max_cap,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Truck":
        return cls(
            dim=data["dimensions"],
            max_cap=data.get("max_capacity", 0),
        )

    def __repr__(self) -> str:
        return f"Truck(Dim:{self.dim}, MaxCap:{self.max_cap})"