from __future__ import annotations

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QPushButton,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from luthelper.domain.models import AppState
from luthelper.presentation.widgets.ui_kit import GhostButton, Pill, SectionHeading, label


class AllCoursesPage(QWidget):
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
                "FULL CATALOG",
                "全校课程查询",
                "进入页面后自动加载完整列表，再在本地筛选。",
            )
        )
        header.addStretch(1)
        header.addWidget(GhostButton("刷新全部课程"))
        root.addLayout(header)

        toolbar = QHBoxLayout()
        self.search = QLineEdit()
        self.search.setPlaceholderText("关键词 / 教师")
        self.search.setClearButtonEnabled(True)
        self.campus = QComboBox()
        self.campus.addItems(["全部校区", "彭家坪校区", "兰工坪校区", "网上学习"])
        toolbar.addWidget(self.search, 1)
        toolbar.addWidget(self.campus)
        toolbar.addWidget(Pill("已加载 · 本地筛选", "live"))
        root.addLayout(toolbar)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["加入", "课程", "余量", "教师", "时间地点", "状态"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 56)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        root.addWidget(self.table, 1)

        footer = QHBoxLayout()
        footer.addWidget(label("全部课程不会带校区参数；关键词只在本地过滤。", role="muted"))
        footer.addStretch(1)
        footer.addWidget(Pill("0 个待加入教学班", "neutral"))
        root.addLayout(footer)
        self._fill_demo()

    def _fill_demo(self) -> None:
        rows = [
            ("A00101", "全校课程占位 001", "教师 A", "01", "21/40", "1-16 周 星期一 第 1-2 节"),
            ("A00101", "全校课程占位 001", "教师 B", "02", "40/40", "1-16 周 星期三 第 5-6 节"),
            ("A00201", "全校课程占位 002", "教师 C", "01", "18/30", "3-12 周 星期二 第 3-4 节"),
            ("A00301", "全校课程占位 003", "教师 D", "01", "29/50", "1-16 周 星期四 第 7-8 节"),
            ("A00401", "全校课程占位 004", "教师 E", "01", "70/80", "1-16 周 星期五 第 9-10 节"),
        ]
        self.table.setRowCount(len(rows))
        for row, (code, name, teacher, class_no, cap, time_text) in enumerate(rows):
            add = QPushButton("+")
            add.setFixedSize(28, 28)
            add.setStyleSheet(
                "QPushButton { color: #147d6d; background: #f1faf6; border: 1px solid #cfe4dc; border-radius: 14px; font-weight: 700; }"
            )
            holder = QWidget()
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(7, 0, 0, 0)
            holder_layout.addWidget(add)
            holder_layout.addStretch(1)
            self.table.setCellWidget(row, 0, holder)
            self.table.setItem(row, 1, QTableWidgetItem(f"{name}\n{code} · 课序号 {class_no}"))
            self.table.setItem(row, 2, QTableWidgetItem(cap))
            self.table.setItem(row, 3, QTableWidgetItem(teacher))
            self.table.setItem(row, 4, QTableWidgetItem(time_text))
            self.table.setItem(row, 5, QTableWidgetItem("已满" if cap.split("/")[0] == cap.split("/")[1] else "可选"))
