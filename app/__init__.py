"""Compatibility shim exposing the FastAPI ``app`` object for ``app:app``.

This project uses ``main.py`` as the canonical application module. To
support running with ``uvicorn app:app`` (historical convention) this
package re-exports the ASGI application object from ``main``.
"""
from main import app  # re-export ASGI app for `uvicorn app:app`

__all__ = ["app"]
