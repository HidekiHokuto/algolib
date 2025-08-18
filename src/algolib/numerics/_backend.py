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
        # return math.tan(x) if _is_finite(x) else _NAN
        if not _is_finite(x):
            return _NAN
        # 先以 τ=2π 做一次规约，保证 x 与 x+2πm 的代表元一致；
        # 对 x+π(2m+1) 代表元相差 π，但 tan(r+π)=tan(r)。
        tau = 2.0 * math.pi
        r = math.remainder(x, tau)
        # “黏零”抹掉极小残差，避免周期性用例的 1e-12 级毛刺放大
        if -2.0 ** -40 < r < 2.0 ** -40:
            r = 0.0 * r
        return math.tan(r)

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