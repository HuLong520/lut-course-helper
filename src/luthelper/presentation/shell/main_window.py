from __future__ import annotations

from PySide6.QtCore import Qt
from qfluentwidgets import InfoBar, InfoBarPosition, setTheme, setThemeColor, Theme

from luthelper.application.demo_data import demo_state
from luthelper.domain.models import AppState, Course, CourseGroup
from luthelper.presentation.pages.all_courses_page import AllCoursesPage
from luthelper.presentation.pages.courses_page import CoursesPage
from luthelper.presentation.pages.selected_page import SelectedPage
from luthelper.presentation.shell.app_shell import AppShell
from luthelper.presentation.theme import tokens


class MainWindow(AppShell):
    def __init__(self) -> None:
        super().__init__(demo_state())
        self.courses_page.setObjectName("coursesPage")
        self.all_courses_page.setObjectName("allCoursesPage")
        self.selected_page.setObjectName("selectedPage")
        self._wire()

    def _wire(self) -> None:
        self.courses_page.courseAdded.connect(self._add_course)
        self.courses_page.courseRemoved.connect(self._remove_course)
        self.courses_page.groupRemoved.connect(self._remove_group)

    def _add_course(self, course: Course) -> None:
        group = next((g for g in self.state.groups if g.course_code == course.course_code), None)
        if group is None:
            group = CourseGroup(course_code=course.course_code, name=course.name)
            self.state.groups.append(group)
        from luthelper.domain.models import TaskInstance

        group.tasks.append(TaskInstance(course=course))
        self.courses_page.set_state(self.state)
        self._toast("已加入抢课队列", f"{course.name} · {course.class_no} 班")

    def _remove_course(self, course: Course) -> None:
        for group in self.state.groups:
            if group.course_code != course.course_code:
                continue
            group.tasks = [task for task in group.tasks if task.course.class_id != course.class_id]
        self.state.groups = [group for group in self.state.groups if group.tasks]
        self.courses_page.set_state(self.state)
        self._toast("已取消加入", f"{course.name} · {course.class_no} 班")

    def _remove_group(self, group: CourseGroup) -> None:
        self.state.groups = [item for item in self.state.groups if item is not group]
        self.courses_page.set_state(self.state)
        self._toast("课程组已删除", group.name)

    def _toast(self, title: str, message: str) -> None:
        InfoBar.success(
            title=title,
            content=message,
            orient=Qt.Orientation.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=4000,
            parent=self,
        )


def create_main_window() -> MainWindow:
    setTheme(Theme.LIGHT)
    setThemeColor(tokens.TEAL)
    return MainWindow()
