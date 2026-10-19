from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QStackedWidget,
    QVBoxLayout,
    QWidget,
)

from luthelper.domain.models import AppState
from luthelper.presentation.pages.all_courses_page import AllCoursesPage
from luthelper.presentation.pages.courses_page import CoursesPage
from luthelper.presentation.pages.selected_page import SelectedPage
from luthelper.presentation.theme import tokens
from luthelper.presentation.widgets.ui_kit import Pill, RoundIconButton, label


class SidebarButton(QPushButton):
    def __init__(self, glyph: str, text: str, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.glyph = glyph
        self.title = text
        self.setCheckable(True)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setMinimumHeight(42)
        self.setText(f"{glyph}   {text}")
        self.setStyleSheet(
            f"""
            QPushButton {{
                color: rgba(222, 239, 231, 0.68);
                background: transparent;
                border: 0;
                border-radius: 9px;
                padding: 8px 11px;
                text-align: left;
                font-size: 12px;
                font-weight: 600;
            }}
            QPushButton:hover {{
                color: #ffffff;
                background: rgba(255, 255, 255, 0.06);
            }}
            QPushButton:checked {{
                color: #ffffff;
                background: rgba(198, 234, 220, 0.13);
                border-left: 3px solid #9ed9c6;
                padding-left: 8px;
            }}
            """
        )


class AppShell(QMainWindow):
    """还原 HTML 原型的应用壳。"""

    def __init__(self, state: AppState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self.setWindowTitle("抢课助手")
        self.resize(1440, 900)
        self.setMinimumSize(1080, 680)
        self._page_buttons: dict[str, SidebarButton] = {}
        self._build_ui()

    def _build_ui(self) -> None:
        root = QWidget()
        self.setCentralWidget(root)
        layout = QHBoxLayout(root)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self._build_sidebar())

        main = QWidget()
        main.setStyleSheet(f"background: {tokens.BG};")
        main_layout = QVBoxLayout(main)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        main_layout.addWidget(self._build_topbar())

        self.stack = QStackedWidget()
        self.courses_page = CoursesPage(self.state)
        self.all_courses_page = AllCoursesPage(self.state)
        self.selected_page = SelectedPage(self.state)
        self.stack.addWidget(self.courses_page)
        self.stack.addWidget(self.all_courses_page)
        self.stack.addWidget(self.selected_page)
        main_layout.addWidget(self.stack, 1)
        layout.addWidget(main, 1)
        self._switch("courses")

    def _build_sidebar(self) -> QWidget:
        sidebar = QWidget()
        sidebar.setFixedWidth(224)
        sidebar.setStyleSheet(
            f"""
            QWidget {{
                background: qlineargradient(x1:0,y1:0,x2:0.3,y2:1,
                    stop:0 {tokens.NAV}, stop:1 {tokens.NAV_DEEP});
            }}
            """
        )
        layout = QVBoxLayout(sidebar)
        layout.setContentsMargins(14, 20, 14, 16)
        layout.setSpacing(6)

        brand = QHBoxLayout()
        mark = QLabel("校")
        mark.setFixedSize(38, 38)
        mark.setAlignment(Qt.AlignmentFlag.AlignCenter)
        mark.setStyleSheet(
            "color:#12372d;background:#d7eee5;border-radius:12px;font-size:17px;font-weight:800;"
        )
        brand.addWidget(mark)
        brand_text = QVBoxLayout()
        brand_text.setSpacing(0)
        name = label("抢课助手")
        name.setStyleSheet("color:#f4fbf7;font-size:15px;font-weight:700;")
        meta = label("LUT HELPER")
        meta.setStyleSheet("color:rgba(220,239,230,0.56);font-size:8px;font-weight:600;")
        brand_text.addWidget(name)
        brand_text.addWidget(meta)
        brand.addLayout(brand_text)
        brand.addStretch(1)
        layout.addLayout(brand)

        spacer = QLabel("工作空间")
        spacer.setStyleSheet("color:rgba(220,239,230,0.42);font-size:9px;padding:12px 8px 4px;")
        layout.addWidget(spacer)

        for key, glyph, title in [
            ("courses", "▤", "课程"),
            ("all-courses", "⌕", "全校课程"),
            ("selected", "▦", "已选课程"),
        ]:
            button = SidebarButton(glyph, title)
            button.clicked.connect(lambda _=False, k=key: self._switch(k))
            self._page_buttons[key] = button
            layout.addWidget(button)

        layout.addStretch(1)
        batch = QLabel(f"当前批次\n{self.state.batch.name if self.state.batch else '未选择'}")
        batch.setStyleSheet(
            "color:#e7f5ee;background:rgba(255,255,255,0.045);"
            "border:1px solid rgba(218,239,230,0.08);border-radius:12px;"
            "padding:10px;font-size:9px;"
        )
        layout.addWidget(batch)
        return sidebar

    def _build_topbar(self) -> QWidget:
        topbar = QWidget()
        topbar.setFixedHeight(72)
        topbar.setStyleSheet(
            f"background:{tokens.SURFACE};border-bottom:1px solid {tokens.LINE};"
        )
        layout = QHBoxLayout(topbar)
        layout.setContentsMargins(24, 0, 20, 0)
        layout.setSpacing(10)

        breadcrumb = QVBoxLayout()
        breadcrumb.setSpacing(0)
        eyebrow = label("LUT HELPER")
        eyebrow.setStyleSheet(f"color:{tokens.MUTED};font-size:9px;font-weight:700;")
        self.breadcrumb_label = label("工作空间 / 课程")
        self.breadcrumb_label.setStyleSheet(f"color:{tokens.INK_SOFT};font-size:11px;font-weight:600;")
        breadcrumb.addWidget(eyebrow)
        breadcrumb.addWidget(self.breadcrumb_label)
        layout.addLayout(breadcrumb)
        layout.addWidget(Pill("在线", "live"))
        layout.addStretch(1)

        batch = QLabel(self.state.batch.name if self.state.batch else "无批次")
        batch.setStyleSheet(
            f"color:{tokens.INK_SOFT};background:{tokens.SURFACE_SOFT};"
            f"border:1px solid {tokens.LINE};border-radius:8px;padding:7px 10px;font-size:10px;"
        )
        layout.addWidget(batch)
        layout.addWidget(RoundIconButton("🔔"))
        layout.addWidget(RoundIconButton("?"))

        user = QLabel(
            f"{self.state.student.name}  ·  {self.state.student.college}"
        )
        user.setStyleSheet(
            f"color:{tokens.INK};background:{tokens.SURFACE_SOFT};"
            f"border:1px solid {tokens.LINE};border-radius:10px;padding:7px 10px;font-size:10px;"
        )
        layout.addWidget(user)
        return topbar

    def _switch(self, key: str) -> None:
        pages = {
            "courses": (self.courses_page, "工作空间 / 课程"),
            "all-courses": (self.all_courses_page, "工作空间 / 全校课程"),
            "selected": (self.selected_page, "工作空间 / 已选课程"),
        }
        page, crumb = pages[key]
        self.stack.setCurrentWidget(page)
        self.breadcrumb_label.setText(crumb)
        for name, button in self._page_buttons.items():
            button.setChecked(name == key)
