from __future__ import annotations

from PySide6.QtGui import QFont
from PySide6.QtWidgets import QApplication

from . import tokens


def apply_theme(app: QApplication) -> None:
    app.setStyle("Fusion")
    font = QFont("Microsoft YaHei UI")
    font.setPointSize(10)
    app.setFont(font)
    app.setStyleSheet(
        f"""
        QWidget {{
            color: {tokens.INK};
            background: transparent;
            font-family: "Segoe UI Variable", "Microsoft YaHei UI", "Segoe UI";
        }}
        QMainWindow, QDialog {{
            background: {tokens.BG};
        }}
        QToolTip {{
            color: #ffffff;
            background: {tokens.INK};
            border: none;
            padding: 5px 8px;
        }}
        QTableWidget {{
            color: {tokens.INK_SOFT};
            background: {tokens.SURFACE};
            alternate-background-color: {tokens.SURFACE_SOFT};
            border: 1px solid {tokens.LINE};
            border-radius: 8px;
            selection-background-color: #dcefe8;
            selection-color: {tokens.INK};
            gridline-color: {tokens.LINE};
        }}
        QTableWidget::item {{
            padding: 5px 8px;
            border: none;
        }}
        QTableWidget::item:selected {{
            color: {tokens.INK};
            background: #dcefe8;
        }}
        QHeaderView::section {{
            color: {tokens.MUTED};
            background: {tokens.SURFACE_SOFT};
            border: none;
            border-bottom: 1px solid {tokens.LINE};
            border-right: 1px solid {tokens.LINE};
            padding: 7px 8px;
            font-size: 10px;
            font-weight: 600;
        }}
        QLineEdit, QComboBox, QSpinBox {{
            min-height: 30px;
            color: {tokens.INK_SOFT};
            background: {tokens.SURFACE_SOFT};
            border: 1px solid {tokens.LINE};
            border-radius: 7px;
            padding: 3px 8px;
        }}
        QLineEdit:focus, QComboBox:focus, QSpinBox:focus {{
            background: #ffffff;
            border-color: #90c8b7;
        }}
        QSplitter::handle:horizontal {{
            width: 8px;
            background: transparent;
        }}
        QScrollBar:vertical {{
            width: 8px;
            margin: 2px;
            background: transparent;
        }}
        QScrollBar::handle:vertical {{
            min-height: 28px;
            background: {tokens.LINE_STRONG};
            border-radius: 4px;
        }}
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
            height: 0;
        }}
        """
    )
