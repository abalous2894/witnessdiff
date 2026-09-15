"""Uvicorn entrypoint for the WitnessDiff API."""

from __future__ import annotations

import os


def main() -> None:
    import uvicorn

    host = os.environ.get("WITNESSDIFF_API_HOST", "127.0.0.1")
    port = int(os.environ.get("WITNESSDIFF_API_PORT", "8080"))
    uvicorn.run(
        "witnessdiff.api.main:app",
        host=host,
        port=port,
        reload=os.environ.get("WITNESSDIFF_API_RELOAD") == "1",
    )


if __name__ == "__main__":
    main()
