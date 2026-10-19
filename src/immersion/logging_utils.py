from __future__ import annotations

import logging
import sys
from pathlib import Path


def configure_logging(app_name: str = "immersion") -> None:
    """Configure a shared logging setup for the application."""
    log_dir = Path.home() / f".{app_name}"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_path = log_dir / "app.log"

    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(
        logging.Formatter(
            fmt="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
    )

    console = logging.StreamHandler(sys.stdout)
    console.setFormatter(handler.formatter)

    logging.basicConfig(level=logging.INFO, handlers=[handler, console])
