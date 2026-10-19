from __future__ import annotations

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QAbstractItemView,
    QComboBox,
    QFrame,
    QHBoxLayout,
    QHeaderView,
    QLineEdit,
    QSpinBox,
    QSplitter,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
    QScrollArea,
    QSizePolicy,
)
from qfluentwidgets import InfoBar, InfoBarPosition

from luthelper.domain.models import AppState, Course, CourseGroup, GroupState, TaskState
from luthelper.presentation.theme import tokens
from luthelper.presentation.widgets.ui_kit import (
    AddButton,
    BottomLogDock,
    Card,
    GhostButton,
    Pill,
    PrimaryButton,
    RoundIconButton,
    SectionHeading,
    label,
)


class CoursesPage(QWidget):
    courseAdded = Signal(object)
    courseRemoved = Signal(object)
    groupRemoved = Signal(object)

    def __init__(self, state: AppState, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.state = state
        self._row_widgets: dict[str, AddButton] = {}
        self._group_cards: dict[str, QFrame] = {}
        self._build_ui()
        self.set_state(state)

    def _build_ui(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(26, 22, 26, 14)
        root.setSpacing(16)

        header = QHBoxLayout()
        header.addWidget(
            SectionHeading(
                "COURSE WORKSPACE",
                "把查课和抢课放在同一张桌面",
                "先选教学班，再编排首选与备选；所有请求状态集中在一处。",
            )
        )
        header.addStretch(1)
        header.addWidget(GhostButton("刷新课程"))
        root.addLayout(header)

        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.addWidget(self._build_course_browser())
        splitter.addWidget(self._build_queue_panel())
        splitter.setStretchFactor(0, 62)
        splitter.setStretchFactor(1, 38)
        splitter.setSizes([820, 500])
        root.addWidget(splitter, 1)
        log = BottomLogDock()
        log.setFixedHeight(116)
        root.addWidget(log)

    def _build_course_browser(self) -> Card:
        card = Card()
        body = card.body()

        top = QHBoxLayout()
        top.addWidget(label("课程检索", role="section"))
        self.course_summary = label("当前轮次 · 7 个教学班", role="muted")
        top.addWidget(self.course_summary)
        top.addStretch(1)
        top.addWidget(RoundIconButton("▦"))
        top.addWidget(RoundIconButton("≡"))
        body.addLayout(top)

        filters = QHBoxLayout()
        type_combo = QComboBox()
        type_combo.addItems(["系统推荐", "方案内", "体育", "公选"])
        campus_combo = QComboBox()
        campus_combo.addItems(["彭家坪校区", "兰工坪校区", "网上学习"])
        search = QLineEdit()
        search.setPlaceholderText("搜索课程名 / 教师")
        search.setClearButtonEnabled(True)
        filters.addWidget(type_combo)
        filters.addWidget(campus_combo)
        filters.addWidget(search, 1)
        filters.setSpacing(7)
        body.addLayout(filters)

        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["加入", "课程", "余量", "教师", "时间地点", "状态"])
        self.table.verticalHeader().setVisible(False)
        self.table.setShowGrid(False)
        self.table.setAlternatingRowColors(True)
        self.table.setSelectionMode(QAbstractItemView.SelectionMode.NoSelection)
        self.table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        self.table.verticalHeader().setDefaultSectionSize(58)
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Fixed)
        self.table.setColumnWidth(0, 58)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents)
        self.table.horizontalHeader().setSectionResizeMode(4, QHeaderView.ResizeMode.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(5, QHeaderView.ResizeMode.ResizeToContents)
        body.addWidget(self.table, 1)
        return card

    def _build_queue_panel(self) -> Card:
        card = Card()
        body = card.body()

        top = QHBoxLayout()
        queue_head = label("抢课队列", role="section")
        queue_head.setStyleSheet(f"color:{tokens.INK};font-size:13px;font-weight:800;")
        top.addWidget(queue_head)
        self.group_count = Pill("0 组", "live")
        top.addWidget(self.group_count)
        top.addStretch(1)
        self.start_all_button = PrimaryButton("开始全部")
        self.start_all_button.setMinimumSize(108, 36)
        self.start_all_button.clicked.connect(self._toggle_all)
        top.addWidget(self.start_all_button)
        body.addLayout(top)

        params = QHBoxLayout()
        params.setSpacing(7)
        params.addWidget(label("间隔", role="muted"))
        self.interval_combo = QComboBox()
        self.interval_combo.addItems(["50 ms", "100 ms", "200 ms", "500 ms"])
        self.interval_combo.setCurrentIndex(1)
        params.addWidget(self.interval_combo)
        params.addWidget(label("每课线程", role="muted"))
        self.thread_spin = QSpinBox()
        self.thread_spin.setRange(1, 20)
        self.thread_spin.setValue(3)
        self.thread_spin.valueChanged.connect(self._refresh_thread_hint)
        self.thread_hint = label("预计 9 线程", role="muted")
        self.thread_hint.setStyleSheet(f"color:{tokens.TEAL};font-size:9px;font-weight:700;")
        params.addWidget(self.thread_spin)
        params.addWidget(self.thread_hint)
        params.addStretch(1)
        body.addLayout(params)

        schedule = QHBoxLayout()
        schedule.setSpacing(6)
        schedule.addWidget(label("定时开抢", role="muted"))
        schedule_date = QLineEdit("2026/10/19")
        schedule_date.setFixedWidth(104)
        schedule_time = QLineEdit("13:28:00")
        schedule_time.setFixedWidth(90)
        schedule.addWidget(schedule_date)
        schedule.addWidget(schedule_time)
        schedule.addStretch(1)
        schedule_status = label("未启用", role="muted")
        schedule_status.setStyleSheet(f"color:{tokens.FAINT};font-size:9px;")
        schedule.addWidget(schedule_status)
        body.addLayout(schedule)

        self.queue_container = QWidget()
        self.queue_layout = QVBoxLayout(self.queue_container)
        self.queue_layout.setContentsMargins(0, 0, 0, 0)
        self.queue_layout.setSpacing(10)
        body.addWidget(self.queue_container, 1)
        return card

    def set_state(self, state: AppState) -> None:
        self.state = state
        self._render_courses()
        self._render_groups()
        self._refresh_start_all()
        self._refresh_thread_hint()

    def _render_courses(self) -> None:
        self.table.setRowCount(len(self.state.courses))
        self._row_widgets.clear()
        for row, course in enumerate(self.state.courses):
            add = AddButton()
            add.set_added(self._is_added(course))
            add.addRequested.connect(lambda c=course: self._request_add(c))
            add.removeRequested.connect(lambda c=course: self._request_remove(c))
            self._row_widgets[course.class_id] = add
            holder = QWidget()
            holder_layout = QHBoxLayout(holder)
            holder_layout.setContentsMargins(7, 0, 0, 0)
            holder_layout.addWidget(add)
            holder_layout.addStretch(1)
            self.table.setCellWidget(row, 0, holder)
            self.table.setItem(row, 1, QTableWidgetItem(f"{course.name}\n{course.course_code} · 课序号 {course.class_no}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{course.selected}/{course.capacity}"))
            self.table.setItem(row, 3, QTableWidgetItem(course.teacher))
            self.table.setItem(row, 4, QTableWidgetItem(course.time_text))
            self.table.setItem(row, 5, QTableWidgetItem("已满" if not course.available else "冲突" if course.conflict else "可选"))

    def _is_added(self, course: Course) -> bool:
        return any(
            group.course_code == course.course_code
            and any(task.course.class_id == course.class_id for task in group.tasks)
            for group in self.state.groups
        )

    def _render_groups(self) -> None:
        while self.queue_layout.count():
            item = self.queue_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        self.group_count.setText(f"{len(self.state.groups)} 组")
        for group in self.state.groups:
            self.queue_layout.addWidget(self._build_group_card(group))
        self.queue_layout.addStretch(1)

    def _request_add(self, course: Course) -> None:
        self.courseAdded.emit(course)
        self._toast("已加入抢课队列", f"{course.name} · {course.class_no} 班")

    def _request_remove(self, course: Course) -> None:
        self.courseRemoved.emit(course)
        self._toast("已取消加入", f"{course.name} · {course.class_no} 班")

    def _refresh_start_all(self) -> None:
        running = any(group.state is GroupState.RUNNING for group in self.state.groups)
        self.start_all_button.setText("全部停止" if running else "开始全部")
        self.start_all_button.setStyleSheet(
            """
            QPushButton {
                color: #ffffff;
                background: #bb4b42;
                border: 1px solid #bb4b42;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover { background: #a84139; border-color: #a84139; }
            """
            if running
            else """
            QPushButton {
                color: #ffffff;
                background: #147d6d;
                border: 1px solid #147d6d;
                border-radius: 8px;
                padding: 6px 14px;
                font-size: 11px;
                font-weight: 700;
            }
            QPushButton:hover { background: #0d675a; border-color: #0d675a; }
            """
        )

    def _refresh_thread_hint(self) -> None:
        active = sum(1 for group in self.state.groups for task in group.tasks if task.state is TaskState.ACTIVE)
        total = max(1, active or len(self.state.groups)) * self.thread_spin.value()
        self.thread_hint.setText(f"预计 {total} 线程")

    def _toggle_all(self) -> None:
        if not self.state.groups:
            InfoBar.warning(
                title="请先选择课程",
                content="请从左表加入至少一个教学班。",
                parent=self,
                position=InfoBarPosition.TOP,
                duration=3500,
            )
            return
        running = any(group.state is GroupState.RUNNING for group in self.state.groups)
        for group in self.state.groups:
            if group.state is GroupState.SUCCESS:
                continue
            for index, task in enumerate(group.tasks):
                task.state = TaskState.PAUSED if running else (TaskState.ACTIVE if index == 0 else TaskState.STANDBY)
        self._render_groups()
        self._refresh_start_all()
        self._toast("已全部停止" if running else "已全部开始", "")

    def _toast(self, title: str, content: str) -> None:
        InfoBar.success(
            title=title,
            content=content,
            parent=self,
            position=InfoBarPosition.TOP,
            duration=3500,
        )

    def _build_group_card(self, group: CourseGroup) -> QFrame:
        card = QFrame()
        card.setStyleSheet(
            f"""
            QFrame {{
                background: {tokens.SURFACE};
                border: 1px solid {tokens.LINE};
                border-radius: 12px;
            }}
            QFrame:hover {{
                border-color: {tokens.LINE_STRONG};
                background: #fffefb;
            }}
            """
        )
        layout = QVBoxLayout(card)
        layout.setContentsMargins(12, 10, 12, 10)
        layout.setSpacing(8)

        head = QHBoxLayout()
        symbol = label(group.course_code[-2:], role="muted")
        symbol.setFixedSize(30, 30)
        symbol.setAlignment(Qt.AlignmentFlag.AlignCenter)
        symbol.setStyleSheet(
            f"color:{tokens.TEAL_STRONG};background:{tokens.TEAL_PALE};"
            "border:1px solid #d3e9df;border-radius:8px;font-size:10px;font-weight:800;"
        )
        head.addWidget(symbol)
        name = label(group.name, role="section")
        name.setStyleSheet(f"color:{tokens.INK};font-size:11px;font-weight:800;")
        head.addWidget(name)
        state_text = {
            GroupState.RUNNING: "运行中",
            GroupState.PAUSED: "已暂停",
            GroupState.SUCCESS: "已成功",
            GroupState.WAITING: "待开始",
        }.get(group.state, "待开始")
        head.addWidget(Pill(state_text, "live" if group.state == GroupState.RUNNING else "neutral"))
        head.addStretch(1)
        head.addWidget(label(f"{len(group.tasks)} 个教学班", role="muted"))
        remove = RoundIconButton("×")
        remove.clicked.connect(lambda _=False, g=group: self._request_group_remove(g))
        head.addWidget(remove)
        layout.addLayout(head)

        for index, task in enumerate(group.tasks):
            task_row = QFrame()
            task_row.setFixedHeight(48)
            task_row.setStyleSheet(
                f"QFrame {{ background:{tokens.SURFACE_SOFT};border:1px solid #e9e5dc;"
                "border-radius:9px; }"
            )
            row = QHBoxLayout(task_row)
            row.setContentsMargins(8, 5, 8, 5)
            row.setSpacing(7)
            role = "首选" if index == 0 else f"备选 {index}"
            role_label = label(f"{'▶' if task.state is TaskState.ACTIVE else '○'}")
            role_label.setStyleSheet(
                f"color:{tokens.TEAL if task.state is TaskState.ACTIVE else tokens.MUTED};"
                "font-size:11px;"
            )
            row.addWidget(role_label)
            copy = QVBoxLayout()
            copy.setSpacing(1)
            main = label(f"{task.course.class_no} 班 · {task.course.teacher}")
            main.setStyleSheet(f"color:{tokens.INK_SOFT};font-size:10px;font-weight:700;")
            main.setFixedHeight(15)
            meta = label(f"{task.course.campus} · {task.course.time_text}")
            meta.setStyleSheet(f"color:{tokens.FAINT};font-size:8px;")
            meta.setFixedHeight(13)
            copy.addWidget(main)
            copy.addWidget(meta)
            row.addLayout(copy, 1)
            role_badge = Pill(role, "live" if index == 0 else "neutral")
            row.addWidget(role_badge)
            row.addWidget(label(f"{task.course.selected}/{task.course.capacity}", role="muted"))
            layout.addWidget(task_row)
        return card

    def _request_group_remove(self, group: CourseGroup) -> None:
        self.groupRemoved.emit(group)
        self._toast("课程组已删除", group.name)
