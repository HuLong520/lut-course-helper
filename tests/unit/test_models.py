from luthelper.application.demo_data import demo_state
from luthelper.domain.models import GroupState, TaskState


def test_demo_state_has_three_pages_of_data() -> None:
    state = demo_state()
    assert len(state.courses) == 7
    assert len(state.groups) == 3
    assert len(state.selected_courses) == 7


def test_group_state_is_derived_from_tasks() -> None:
    state = demo_state()
    group = state.groups[0]
    assert group.state is GroupState.WAITING
    group.tasks[0].state = TaskState.ACTIVE
    assert group.state is GroupState.RUNNING
    group.tasks[0].state = TaskState.SUCCESS
    assert group.state is GroupState.SUCCESS


def test_single_class_group_is_supported() -> None:
    state = demo_state()
    assert len(state.groups[2].tasks) == 1
