"""Package shim that lazily re-exports the ASGI application.

This avoids importing ``main`` at package import time, preventing circular
imports during development with auto-reload. When ``app`` attribute is
accessed (e.g. ``uvicorn app:app``), the shim will import ``main`` and
return the application object.
"""
from importlib import import_module
from typing import Any

__all__ = ["app"]


def __getattr__(name: str) -> Any:
    if name == "app":
        mod = import_module("main")
        return getattr(mod, "app")
    raise AttributeError(f"module {__name__} has no attribute {name}")
