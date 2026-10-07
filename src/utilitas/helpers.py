from __future__ import annotations

import dataclasses
import time
from typing import Any, Dict


def _now() -> float:
    return time.perf_counter()


def asdict_safe(params: Any) -> Dict[str, Any]:
    if params is None:
        return {}
    if dataclasses.is_dataclass(params) and not isinstance(params, type):
        return dataclasses.asdict(params)
    to_dict = getattr(params, "to_dict", None)
    if callable(to_dict):
        return dict(to_dict())
    if hasattr(params, "__dict__"):
        return {k: v for k, v in vars(params).items() if not k.startswith("_")}
    return dict(params)