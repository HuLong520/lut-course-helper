from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any
from uuid import uuid4


class TaskState(StrEnum):
    STANDBY = "standby"
    ACTIVE = "active"
    PAUSED = "paused"
    SUCCESS = "success"
    FAILED = "failed"
    STOPPED = "stopped"


class GroupState(StrEnum):
    WAITING = "waiting"
    RUNNING = "running"
    PAUSED = "paused"
    SUCCESS = "success"
    STOPPED = "stopped"
    FAILED = "failed"


class RobKind(StrEnum):
    SUCCESS = "success"
    QUEUED = "queued"
    PENDING_CONFIRMATION = "pending_confirmation"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    STOPPED = "stopped"


class UnavailableKind(StrEnum):
    CAPACITY_FULL = "capacity_full"
    CHECK_FAILED = "check_failed"
    CONFLICT = "conflict"
    SESSION_EXPIRED = "session_expired"
    UNKNOWN = "unknown"


@dataclass(slots=True)
class CourseSlot:
    weekday: int | None = None
    start_section: int | None = None
    end_section: int | None = None
    weeks: str | None = None
    week_mask: str | None = None
    place: str = ""
    raw_text: str = ""


@dataclass(slots=True)
class Course:
    course_code: str
    name: str
    teacher: str = ""
    class_id: str = ""
    class_no: str = ""
    campus: str = ""
    credits: str = ""
    hours: str = ""
    selected: int = 0
    capacity: int = 0
    conflict: bool = False
    secret_val: str = ""
    time_text: str = ""
    nature: str = ""
    department: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    slots: list[CourseSlot] = field(default_factory=list)

    @property
    def available(self) -> bool:
        return self.capacity <= 0 or self.selected < self.capacity


@dataclass(slots=True)
class SelectedCourse:
    course_code: str
    name: str
    teacher: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
    slots: list[CourseSlot] = field(default_factory=list)


@dataclass(slots=True)
class TaskInstance:
    course: Course
    id: str = field(default_factory=lambda: uuid4().hex)
    state: TaskState = TaskState.STANDBY
    attempts: int = 0
    last_error: str = ""


@dataclass(slots=True)
class CourseGroup:
    course_code: str
    name: str
    tasks: list[TaskInstance] = field(default_factory=list)
    collapsed: bool = False
    success_task: str = ""
    success_time: str = ""

    @property
    def state(self) -> GroupState:
        states = {task.state for task in self.tasks}
        if TaskState.SUCCESS in states:
            return GroupState.SUCCESS
        if TaskState.ACTIVE in states:
            return GroupState.RUNNING
        if states and states <= {TaskState.PAUSED, TaskState.STOPPED}:
            return GroupState.PAUSED
        if TaskState.FAILED in states:
            return GroupState.FAILED
        return GroupState.WAITING


@dataclass(slots=True)
class Student:
    name: str = ""
    username: str = ""
    college: str = ""
    major: str = ""


@dataclass(slots=True)
class Batch:
    code: str
    name: str
    can_select: bool = True
    need_confirm: bool = False


@dataclass(slots=True)
class AppState:
    student: Student = field(default_factory=Student)
    batch: Batch | None = None
    groups: list[CourseGroup] = field(default_factory=list)
    courses: list[Course] = field(default_factory=list)
    selected_courses: list[SelectedCourse] = field(default_factory=list)
    interval_ms: int = 100
    threads: int = 3
    auto_stop: bool = True


@dataclass(slots=True)
class RobOutcome:
    kind: RobKind
    message: str = ""
    raw_text: str = ""
    attempts: int = 0
    duration_ms: int = 0
    unavailable_kind: UnavailableKind | None = None
