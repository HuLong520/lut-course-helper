from __future__ import annotations

from luthelper.presentation.shell.main_window import create_main_window


def test_main_window_starts_with_three_pages(qtbot) -> None:
    window = create_main_window()
    qtbot.addWidget(window)
    window.show()
    qtbot.waitExposed(window)
    assert window.width() >= 1080
    assert window.height() >= 680
    assert window.courses_page.objectName() == "coursesPage"
    assert window.all_courses_page.objectName() == "allCoursesPage"
    assert window.selected_page.objectName() == "selectedPage"
    window.close()


def test_course_can_be_added_and_removed(qtbot) -> None:
    window = create_main_window()
    qtbot.addWidget(window)
    window.show()
    course = window.state.courses[4]
    original_groups = len(window.state.groups)
    window._add_course(course)
    assert len(window.state.groups) >= original_groups
    window._remove_course(course)
    assert all(
        task.course.class_id != course.class_id
        for group in window.state.groups
        for task in group.tasks
    )
    window.close()
