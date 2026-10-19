from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QBrush
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from PySide6.QtWidgets import QLabel

from luthelper.domain.models import AppState
from luthelper.presentation.theme import tokens
from luthelper.presentation.widgets.ui_kit import Card, GhostButton, Pill, SectionHeading, label


class SelectedPage(QWidget):
    def __init__(self, state: AppState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 18)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(
            SectionHeading(
                "MY TIMETABLE",
                "已选课程与课表",
                "左侧核对课程，右侧查看周网格；冲突和未排入课程不会被隐藏。",
            )
        )
        header.addStretch(1)
        header.addWidget(GhostButton("刷新"))
        root.addLayout(header)

        content = QHBoxLayout()
        content.setSpacing(14)
        content.addWidget(self._build_selected_list(), 42)
        content.addWidget(self._build_timetable(), 58)
        root.addLayout(content, 1)

    def _build_selected_list(self) -> Card:
        card = Card()
        body = card.body()
        head = QHBoxLayout()
        head.addWidget(label("已选课程", role="section"))
        head.addWidget(Pill("7 门 · 2 处冲突", "warn"))
        head.addStretch(1)
        body.addLayout(head)

        table = QTableWidget(len(self.state.selected_courses), 3)
        table.setHorizontalHeaderLabels(["课程", "教师", "星期 / 节次"])
        table.verticalHeader().setVisible(False)
        table.setShowGrid(False)
        table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        for row, course in enumerate(self.state.selected_courses):
            table.setItem(row, 0, QTableWidgetItem(f"{course.name}\n{course.course_code}"))
            table.setItem(row, 1, QTableWidgetItem(course.teacher))
            slot = course.slots[0]
            table.setItem(row, 2, QTableWidgetItem(f"星期{slot.weekday} · 第 {slot.start_section}-{slot.end_section} 节"))
        body.addWidget(table, 1)
        body.addWidget(label("退课记录（折叠）", role="muted"))
        return card

    def _build_timetable(self) -> Card:
        card = Card()
        body = card.body()
        head = QHBoxLayout()
        head.addWidget(label("周课表", role="section"))
        head.addStretch(1)
        week = QComboBox()
        week.addItems(["全部周次", *[f"第 {i} 周" for i in range(1, 21)]])
        head.addWidget(week)
        body.addLayout(head)

        grid = QTableWidget(12, 7)
        grid.setHorizontalHeaderLabels(["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"])
        grid.setVerticalHeaderLabels([f"{i}" for i in range(1, 13)])
        grid.verticalHeader().setDefaultSectionSize(37)
        grid.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        grid.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        grid.setShowGrid(True)
        block_colors = [
            ("#e7f2ed", "#c8ded5"),
            ("#fbf1df", "#eeddbb"),
            ("#eaf2f8", "#cedfe9"),
            ("#f9eae7", "#ecd4cf"),
            ("#f1edf6", "#ddd5e8"),
            ("#edf0ef", "#d9dfdc"),
            ("#e7f2ed", "#c8ded5"),
        ]

        for index, course in enumerate(self.state.selected_courses):
            slot = course.slots[0]
            if not slot.weekday or not slot.start_section:
                continue
            row = slot.start_section - 1
            col = slot.weekday - 1
            span = max(1, (slot.end_section or slot.start_section) - slot.start_section + 1)
            if row + span > 12:
                span = 12 - row
            grid.setSpan(row, col, span, 1)
            bg, border = block_colors[index % len(block_colors)]
            block = QLabel(f"{course.name}\n{course.teacher} · {slot.place}")
            block.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
            block.setContentsMargins(6, 4, 6, 4)
            block.setStyleSheet(
                f"QLabel {{ color:{tokens.INK};background:{bg};border:1px solid {border};"
                "border-left:3px solid #438b76;border-radius:6px;padding:4px 6px;font-size:9px; }}"
            )
            grid.setCellWidget(row, col, block)
        body.addWidget(grid, 1)
        return card
