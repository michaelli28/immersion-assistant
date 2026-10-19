from __future__ import annotations

from typing import List

from PySide6 import QtCore, QtGui, QtWidgets

from immersion.ui.overlay_model import OverlaySpan


class OverlayWindow(QtWidgets.QWidget):
    """Semi-transparent overlay that renders translated spans."""

    def __init__(self) -> None:
        window_flags = (
            QtCore.Qt.WindowStaysOnTopHint
            | QtCore.Qt.FramelessWindowHint
            | QtCore.Qt.Tool
        )
        super().__init__(None, window_flags)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, True)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground, True)
        self.spans: List[OverlaySpan] = []

    def update_spans(self, spans: List[OverlaySpan]) -> None:
        self.spans = spans
        self.update()

    def paintEvent(self, event: QtGui.QPaintEvent) -> None:
        painter = QtGui.QPainter(self)
        painter.setRenderHint(QtGui.QPainter.Antialiasing)

        for span in self.spans:
            x, y, w, h = span.bbox
            rect = QtCore.QRectF(x, y, w, h)
            painter.setBrush(QtGui.QColor(0, 0, 0, 160))
            painter.setPen(QtCore.Qt.NoPen)
            painter.drawRoundedRect(rect, 6, 6)

            text = span.translated_text
            if span.pinyin:
                text = f"{text}\n{span.pinyin}"
            painter.setPen(QtGui.QColor("white"))
            painter.drawText(rect.adjusted(8, 8, -8, -8), QtCore.Qt.AlignLeft | QtCore.Qt.AlignTop, text)
