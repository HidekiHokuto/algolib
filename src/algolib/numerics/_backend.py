# src/algolib/numerics/_backend.py

from __future__ import annotations
import math
from typing import Protocol, Optional, Dict

class TrigBackend(Protocol):
    name: str
    def sin(self, x: float) -> float: ...
    def cos(self, x: float) -> float: ...
    def tan(self, x: float) -> float: ...

_NAN = float("nan")

def _is_finite(x: float) -> bool:
    return x == x and x != float("inf") and x != float("-inf")

class SystemTrigBackend:
    name = "system"
    def sin(self, x: float) -> float:
        return math.sin(x) if _is_finite(x) else _NAN
    def cos(self, x: float) -> float:
        return math.cos(x) if _is_finite(x) else _NAN
    def tan(self, x: float) -> float:
        return math.tan(x) if _is_finite(x) else _NAN

# 初始只注册 system，pure 延迟加载
_BACKENDS: Dict[str, TrigBackend] = {
    "system": SystemTrigBackend(),
}
_CURRENT: TrigBackend = _BACKENDS["system"]

def set_backend(name: str) -> None:
    global _CURRENT
    if name in _BACKENDS:
        _CURRENT = _BACKENDS[name]
        return
    if name == "pure":
        # 延迟导入，避免未使用时计入覆盖率
        from . import trig_pure as _pure  # type: ignore
        class PureTrigBackend:
            name = "pure"
            def sin(self, x: float) -> float:
                return _pure.sin(x) if _is_finite(x) else _NAN
            def cos(self, x: float) -> float:
                return _pure.cos(x) if _is_finite(x) else _NAN
            def tan(self, x: float) -> float:
                return _pure.tan(x) if _is_finite(x) else _NAN
        _BACKENDS["pure"] = PureTrigBackend()
        _CURRENT = _BACKENDS["pure"]
        return
    raise ValueError(f"unknown numerics backend: {name!r}")

def get_backend() -> TrigBackend:
    return _CURRENT

def get_backend_name() -> str:
    return _CURRENT.name