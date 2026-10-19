from __future__ import annotations

import threading
import time

from PySide6 import QtCore, QtWidgets

from immersion.app import ImmersionApp
from immersion.ui.overlay_window import OverlayWindow


class ImmersionDesktop:
    """Launch Qt overlay and background pipeline side by side."""

    def __init__(self) -> None:
        self.app = ImmersionApp()
        self.qt_app = QtWidgets.QApplication([])
        self.overlay = OverlayWindow()
        self.overlay.showFullScreen()

        self._thread = threading.Thread(target=self._run_pipeline, daemon=True)

    def start(self) -> None:
        self._thread.start()
        self._refresh_loop()

    def _run_pipeline(self) -> None:
        self.app.start(interval=3.0)

    def _refresh_loop(self) -> None:
        def refresh() -> None:
            self.overlay.update_spans(self.app.state.overlay_spans)
            QtWidgets.QApplication.processEvents()
            QtCore.QTimer.singleShot(500, refresh)

        refresh()
        self.qt_app.exec()


def run_desktop() -> None:
    ImmersionDesktop().start()


if __name__ == "__main__":
    run_desktop()
