from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPainterPath, QPen
from PySide6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)
from qfluentwidgets import CardWidget, PrimaryPushButton, PushButton, TransparentToolButton

from luthelper.presentation.theme import tokens


def label(text: str = "", *, role: str = "body", wrap: bool = False) -> QLabel:
    widget = QLabel(text)
    widget.setWordWrap(wrap)
    widget.setProperty("role", role)
    widget.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
    return widget


class Card(CardWidget):
    def __init__(self, parent: QWidget | None = None, *, padding: int = 16) -> None:
        super().__init__(parent)
        self.setObjectName("card")
        self.setStyleSheet(
            f"""
            QFrame#card {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.LINE};
                border-radius: 16px;
            }}
            """
        )
        self._layout = QVBoxLayout(self)
        self._layout.setContentsMargins(padding, padding, padding, padding)
        self._layout.setSpacing(10)

    def body(self) -> QVBoxLayout:
        return self._layout


class Pill(QLabel):
    def __init__(self, text: str, tone: str = "neutral", parent: QWidget | None = None) -> None:
        super().__init__(text, parent)
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        self.setMaximumHeight(24)
        self.set_tone(tone)

    def set_tone(self, tone: str) -> None:
        palette = {
            "live": (tokens.TEAL_PALE, tokens.TEAL_STRONG, "#cfe7dd"),
            "warn": (tokens.AMBER_SOFT, tokens.AMBER, "#f1dfba"),
            "danger": (tokens.RED_SOFT, tokens.RED, "#efd4d0"),
            "neutral": (tokens.SURFACE_SOFT, tokens.MUTED, tokens.LINE),
        }
        bg, fg, border = palette.get(tone, palette["neutral"])
        self.setStyleSheet(
            f"""
            QLabel {{
                color: {fg};
                background: {bg};
                border: 1px solid {border};
                border-radius: 10px;
                padding: 3px 8px;
                font-size: 10px;
                font-weight: 600;
            }}
            """
        )


class PrimaryButton(PrimaryPushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(34)
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: #ffffff;
                background: {tokens.TEAL};
                border: 1px solid {tokens.TEAL};
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }}
            QPushButton:hover {{
                background: {tokens.TEAL_STRONG};
                border-color: {tokens.TEAL_STRONG};
            }}
            QPushButton:pressed {{
                background: #0a594e;
            }}
            QPushButton:disabled {{
                color: #f1f4f2;
                background: #a7c3b9;
                border-color: #a7c3b9;
            }}
            """
        )


class GhostButton(PushButton):
    def __init__(self, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText(text)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(32)
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {tokens.INK_SOFT};
                background: {tokens.SURFACE};
                border: 1px solid {tokens.LINE_STRONG};
                border-radius: 8px;
                padding: 5px 11px;
                font-size: 10px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: {tokens.INK};
                border-color: #bfc8c2;
                background: #ffffff;
            }}
            """
        )


class AddButton(QPushButton):
    addRequested = Signal()
    removeRequested = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._added = False
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.clicked.connect(self._on_click)
        self._refresh()

    @property
    def added(self) -> bool:
        return self._added

    def set_added(self, value: bool) -> None:
        if self._added == value:
            return
        self._added = value
        self._refresh()

    def _on_click(self) -> None:
        if self._added:
            self.removeRequested.emit()
        else:
            self.addRequested.emit()

    def _refresh(self) -> None:
        self.setToolTip("再次点击取消加入" if self._added else "加入抢课队列")
        self.update()

    def paintEvent(self, event) -> None:
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        rect = self.rect().adjusted(5, 5, -5, -5)
        if self._added:
            painter.setPen(Qt.PenStyle.NoPen)
            painter.setBrush(QColor(tokens.TEAL))
            painter.drawEllipse(rect)
            pen = QPen(QColor("#ffffff"), 1.8)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            path = QPainterPath()
            path.moveTo(rect.left() + 5, rect.center().y())
            path.lineTo(rect.center().x() - 1, rect.bottom() - 5)
            path.lineTo(rect.right() - 4, rect.top() + 6)
            painter.drawPath(path)
        else:
            painter.setPen(QPen(QColor("#b9dccc"), 1))
            painter.setBrush(QColor(tokens.TEAL_PALE))
            painter.drawEllipse(rect)
            pen = QPen(QColor(tokens.TEAL_STRONG), 1.5)
            pen.setCapStyle(Qt.PenCapStyle.RoundCap)
            painter.setPen(pen)
            cx, cy = rect.center().x(), rect.center().y()
            painter.drawLine(cx - 4, cy, cx + 4, cy)
            painter.drawLine(cx, cy - 4, cx, cy + 4)


class RoundIconButton(TransparentToolButton):
    def __init__(self, glyph: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setText(glyph)
        self.setFixedSize(28, 28)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: {tokens.MUTED};
                background: transparent;
                border: 0;
                border-radius: 6px;
                font-size: 15px;
            }}
            QPushButton:hover {{
                color: {tokens.INK};
                background: {tokens.SURFACE_SOFT};
            }}
            """
        )


class SectionHeading(QWidget):
    def __init__(self, kicker: str, title: str, subtitle: str = "", parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(3)
        kicker_label = label(kicker.upper(), role="kicker")
        kicker_label.setStyleSheet(f"color: {tokens.TEAL}; font-size: 9px; font-weight: 800; letter-spacing: 1px;")
        title_label = label(title, role="title")
        title_label.setStyleSheet(
            f"color: {tokens.INK}; font-size: 23px; font-weight: 700; letter-spacing: -0.5px;"
        )
        layout.addWidget(kicker_label)
        layout.addWidget(title_label)
        if subtitle:
            layout.addWidget(label(subtitle, role="muted"))


class BottomLogDock(QFrame):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("logDock")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 12)
        layout.setSpacing(6)
        header = QHBoxLayout()
        header.addWidget(label("请求日志", role="section"))
        header.addStretch(1)
        header.addWidget(Pill("8 条记录", "live"))
        header.addWidget(GhostButton("导出"))
        header.addWidget(GhostButton("清空"))
        layout.addLayout(header)
        self.body = QLabel("请求响应将在这里实时显示。")
        self.body.setStyleSheet(
            f"""
            QLabel {{
                color: {tokens.INK_SOFT};
                background: {tokens.SURFACE_SOFT};
                border: 1px solid {tokens.LINE};
                border-radius: 8px;
                padding: 10px;
                font-family: "Cascadia Mono", "Consolas";
                font-size: 10px;
            }}
            """
        )
        self.body.setMinimumHeight(84)
        layout.addWidget(self.body)
