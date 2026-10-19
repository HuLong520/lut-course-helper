from __future__ import annotations

from PySide6.QtCore import Qt
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

from luthelper.domain.models import AppState
from luthelper.presentation.widgets.ui_kit import Card, GhostButton, Pill, SectionHeading, label


class SelectedPage(QWidget):
    def __init__(self, state: AppState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._build_ui()

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 18, 24, 18)
        root.setSpacing(14)

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

        for course in self.state.selected_courses:
            slot = course.slots[0]
            if not slot.weekday or not slot.start_section:
                continue
            row = slot.start_section - 1
            col = slot.weekday - 1
            span = max(1, (slot.end_section or slot.start_section) - slot.start_section + 1)
            if row + span > 12:
                span = 12 - row
            grid.setSpan(row, col, span, 1)
            item = QTableWidgetItem(f"{course.name}\n{course.teacher} · {slot.place}")
            item.setBackground(Qt.GlobalColor.transparent)
            grid.setItem(row, col, item)
        body.addWidget(grid, 1)
        return card
