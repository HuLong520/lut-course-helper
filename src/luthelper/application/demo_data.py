from __future__ import annotations

from luthelper.domain.models import (
    AppState,
    Batch,
    Course,
    CourseGroup,
    CourseSlot,
    SelectedCourse,
    Student,
    TaskInstance,
)


def demo_state() -> AppState:
    courses = [
        Course(
            course_code="C02005",
            name="课程名称占位 A",
            teacher="教师甲",
            class_id="202620271C0200501",
            class_no="01",
            campus="彭家坪校区",
            credits="1.0",
            hours="20",
            selected=15,
            capacity=15,
            time_text="3-12 周 星期日 第 7-8 节",
            nature="公共选修课",
            department="开课单位占位",
        ),
        Course(
            course_code="C02005",
            name="课程名称占位 A",
            teacher="教师乙",
            class_id="202620271C0200502",
            class_no="02",
            campus="彭家坪校区",
            credits="1.0",
            hours="20",
            selected=12,
            capacity=15,
            time_text="3-12 周 星期六 第 5-6 节",
            nature="公共选修课",
            department="开课单位占位",
        ),
        Course(
            course_code="C03108",
            name="课程名称占位 B",
            teacher="教师丙",
            class_id="202620271C0310801",
            class_no="01",
            campus="彭家坪校区",
            credits="2.0",
            hours="32",
            selected=38,
            capacity=40,
            conflict=True,
            time_text="1-8 周 星期一 第 3-4 节",
            nature="专业选修课",
            department="开课单位占位",
        ),
        Course(
            course_code="C03108",
            name="课程名称占位 B",
            teacher="教师丁",
            class_id="202620271C0310802",
            class_no="02",
            campus="兰工坪校区",
            credits="2.0",
            hours="32",
            selected=40,
            capacity=40,
            time_text="1-8 周 星期三 第 3-4 节",
            nature="专业选修课",
            department="开课单位占位",
        ),
        Course(
            course_code="C04201",
            name="课程名称占位 C",
            teacher="教师戊",
            class_id="202620271C0420101",
            class_no="01",
            campus="彭家坪校区",
            credits="1.5",
            hours="24",
            selected=27,
            capacity=30,
            time_text="5-16 周 星期二 第 9-10 节",
            nature="通识教育课",
            department="开课单位占位",
        ),
        Course(
            course_code="C05302",
            name="课程名称占位 D",
            teacher="教师己",
            class_id="202620271C0530201",
            class_no="01",
            campus="彭家坪校区",
            credits="2.0",
            hours="32",
            selected=8,
            capacity=35,
            conflict=True,
            time_text="9-16 周 星期四 第 5-6 节",
            nature="学科基础课",
            department="开课单位占位",
        ),
        Course(
            course_code="C06401",
            name="课程名称占位 E",
            teacher="教师庚",
            class_id="202620271C0640101",
            class_no="01",
            campus="网上学习",
            credits="1.0",
            hours="16",
            selected=48,
            capacity=80,
            time_text="1-16 周 星期五 第 7-8 节",
            nature="公共选修课",
            department="开课单位占位",
        ),
    ]

    group_a = CourseGroup(
        course_code="C02005",
        name="课程名称占位 A",
        tasks=[
            TaskInstance(course=courses[0]),
            TaskInstance(course=courses[1]),
        ],
    )
    group_b = CourseGroup(
        course_code="C03108",
        name="课程名称占位 B",
        tasks=[
            TaskInstance(course=courses[2]),
            TaskInstance(course=courses[3]),
        ],
    )
    group_c = CourseGroup(
        course_code="C04201",
        name="课程名称占位 C",
        tasks=[TaskInstance(course=courses[4])],
    )

    selected = [
        SelectedCourse(
            course_code="S00101",
            name="已选课程占位 A",
            teacher="教师 1",
            slots=[
                CourseSlot(
                    weekday=1,
                    start_section=1,
                    end_section=2,
                    weeks="1-16",
                    week_mask="11111111111111110000",
                    place="教学楼 A101",
                    raw_text="1-16 周 星期一 第 1-2 节 教学楼 A101",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00201",
            name="已选课程占位 B",
            teacher="教师 2",
            slots=[
                CourseSlot(
                    weekday=1,
                    start_section=3,
                    end_section=4,
                    weeks="1-12",
                    week_mask="11111111111100000000",
                    place="教学楼 B203",
                    raw_text="1-12 周 星期一 第 3-4 节 教学楼 B203",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00301",
            name="已选课程占位 C",
            teacher="教师 3",
            slots=[
                CourseSlot(
                    weekday=2,
                    start_section=5,
                    end_section=6,
                    weeks="3-16",
                    week_mask="00111111111111110000",
                    place="教学楼 C305",
                    raw_text="3-16 周 星期二 第 5-6 节 教学楼 C305",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00401",
            name="已选课程占位 D",
            teacher="教师 4",
            slots=[
                CourseSlot(
                    weekday=3,
                    start_section=3,
                    end_section=4,
                    weeks="1-16",
                    week_mask="11111111111111110000",
                    place="实验楼 D108",
                    raw_text="1-16 周 星期三 第 3-4 节 实验楼 D108",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00501",
            name="已选课程占位 E",
            teacher="教师 5",
            slots=[
                CourseSlot(
                    weekday=4,
                    start_section=7,
                    end_section=8,
                    weeks="5-16",
                    week_mask="00001111111111110000",
                    place="教学楼 A207",
                    raw_text="5-16 周 星期四 第 7-8 节 教学楼 A207",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00601",
            name="已选课程占位 F",
            teacher="教师 6",
            slots=[
                CourseSlot(
                    weekday=5,
                    start_section=9,
                    end_section=10,
                    weeks="1-8",
                    week_mask="11111111000000000000",
                    place="教学楼 E110",
                    raw_text="1-8 周 星期五 第 9-10 节 教学楼 E110",
                )
            ],
        ),
        SelectedCourse(
            course_code="S00701",
            name="已选课程占位 G",
            teacher="教师 7",
            slots=[
                CourseSlot(
                    weekday=6,
                    start_section=11,
                    end_section=12,
                    weeks="1-16",
                    week_mask="11111111111111110000",
                    place="教学楼 F401",
                    raw_text="1-16 周 星期六 第 11-12 节 教学楼 F401",
                )
            ],
        ),
    ]

    return AppState(
        student=Student(
            name="示例同学",
            username="2024********",
            college="计算机与人工智能学院",
            major="物联网工程",
        ),
        batch=Batch(code="2026FALL", name="2026 年秋季学期正选"),
        groups=[group_a, group_b, group_c],
        courses=courses,
        selected_courses=selected,
    )
