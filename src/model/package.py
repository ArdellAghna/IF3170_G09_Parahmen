from __future__ import annotations

import itertools
from copy import deepcopy
from typing import Any, Dict, Optional, Tuple

AXES: Tuple[str, str, str] = ("x", "y", "z")

VALID_ORIENTATIONS: Tuple[Tuple[str, str, str], ...] = tuple(
    itertools.permutations(AXES)
)

ROTATION_SWAP: Dict[str, Tuple[str, str]] = {
    "z": ("w", "l"),
    "x": ("l", "h"),
    "y": ("w", "h"),
}


class Package:
    def __init__(
        self,
        pkg_id: str,
        dim: Optional[Dict[str, int]] = None,
        val: float = 0,
        w: float = 0,
        is_fragile: bool = False,
        eta: int = 0,
        *,
        dimensions: Optional[Dict[str, int]] = None,
        value: Optional[float] = None,
        weight: Optional[float] = None,
        position: Optional[Tuple[int, int, int]] = None,
        orientation: Optional[Dict[str, str]] = None,
    ) -> None:
        if dim is not None and dimensions is not None:
            raise ValueError("Package: isi hanya salah satu dari dim/dimensions")
        if dim is None:
            dim = dimensions
        if dim is None:
            dim = {"w": 1, "l": 1, "h": 1}

        self.id: str = pkg_id
        self.og_dim: Dict[str, int] = dict(dim)
        self.cur_dim: Dict[str, int] = dict(dim)
        self.val: float = value if value is not None else val
        self.w: float = weight if weight is not None else w
        self.is_fragile: bool = is_fragile
        self.eta: int = eta

        self.orient: Dict[str, str] = (
            dict(orientation) if orientation is not None else {"w": "x", "l": "y", "h": "z"}
        )
        if tuple(self.orient[s] for s in ("w", "l", "h")) not in VALID_ORIENTATIONS:
            raise ValueError(f"Package: orientasi tidak valid {self.orient}")

        self.position: Optional[Tuple[int, int, int]] = position

    #properti
    @property
    def is_inside(self) -> bool:
        return self.position is not None

    @property
    def eff_dims(self) -> Dict[str, int]:
        return self.cur_dim

    @property
    def oriented_dims(self) -> Tuple[int, int, int]:
        return (self.cur_dim["w"], self.cur_dim["l"], self.cur_dim["h"])

    #operasi
    def rotate(self, axis: str) -> "Package":
        if axis not in ROTATION_SWAP:
            raise ValueError(f"Package.rotate: sumbu harus x/y/z, dapat {axis!r}")
        side_a, side_b = ROTATION_SWAP[axis]
        # Tukar ukuran dua sisi.
        self.cur_dim[side_a], self.cur_dim[side_b] = (
            self.cur_dim[side_b],
            self.cur_dim[side_a],
        )
        # Tukar label orientasi dua sisi.
        self.orient[side_a], self.orient[side_b] = (
            self.orient[side_b],
            self.orient[side_a],
        )
        return self

    def set_orientation(self, orientation: Dict[str, str]) -> "Package":
        if tuple(orientation[s] for s in ("w", "l", "h")) not in VALID_ORIENTATIONS:
            raise ValueError(f"Package: orientasi tidak valid {orientation}")
        self.orient = dict(orientation)
        # sisi yang menghadap masing-masing sumbu kartesian.
        side_of_axis = {axis: side for side, axis in self.orient.items()}
        self.cur_dim = {
            "w": self.og_dim[side_of_axis["x"]],
            "l": self.og_dim[side_of_axis["y"]],
            "h": self.og_dim[side_of_axis["z"]],
        }
        return self

    def copy(self) -> "Package":
        return deepcopy(self)

    #JSON
    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "dimensions": dict(self.og_dim),
            "orientation": dict(self.orient),
            "cur_dim": dict(self.cur_dim),
            "value": self.val,
            "weight": self.w,
            "is_fragile": self.is_fragile,
            "eta": self.eta,
            "position": None if self.position is None else list(self.position),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Package":
        pkg = cls(
            pkg_id=data["id"],
            dim=data["dimensions"],
            val=data.get("value", 0),
            w=data.get("weight", 0),
            is_fragile=data.get("is_fragile", False),
            eta=data.get("eta", 0),
            position=None if data.get("position") is None else tuple(data["position"]),
            orientation=data.get("orientation"),
        )
        return pkg

    def __repr__(self) -> str:
        inside = "" if self.position is None else f" @{tuple(self.position)}"
        return (
            f"Package({self.id}, Dim:{self.cur_dim}, Orient:{self.orient}, "
            f"Val:{self.val}, W:{self.w}, Fragile:{self.is_fragile}, "
            f"ETA:{self.eta}{inside})"
        )