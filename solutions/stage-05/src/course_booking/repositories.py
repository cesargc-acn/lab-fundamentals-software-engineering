"""Where the data lives, described as what the service needs to ask for.

The two protocols are the interesting part. They are written from the point of
view of the caller: the service says "give me the course with this id", not
"run this query". Everything below them is one possible answer.

Stage 2, first half. Two protocols and two dict-backed implementations of them.
The rule that catches most people is at the bottom of every implementation
TODO: hand out copies, never the stored object.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Protocol

from .domain.models import Course, Enrollment


class CourseRepository(Protocol):
    """Where courses are kept."""

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        ...

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join."""
        ...

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        ...


class EnrollmentRepository(Protocol):
    """Where enrollments are kept."""

    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        ...

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        ...


class InMemoryCourseRepository:
    """A dict pretending to be a database. Good enough for a lab and for tests."""

    def __init__(self, courses: Optional[Iterable[Course]] = None) -> None:
        self._courses: Dict[str, Course] = {}
        for course in courses or ():
            self.save(course)

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        stored = self._courses.get(course_id)
        return replace(stored) if stored is not None else None

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join, ordered by id."""
        return [
            replace(course)
            for course in sorted(self._courses.values(), key=lambda c: c.course_id)
            if course.course_type == "free" or course.seats_left > 0
        ]

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        self._courses[course.course_id] = replace(course)


class InMemoryEnrollmentRepository:
    """The same trick for enrollments."""

    def __init__(self) -> None:
        self._enrollments: Dict[str, Enrollment] = {}

    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        self._enrollments[enrollment.enrollment_id] = enrollment

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        return any(
            enrollment.course_id == course_id and enrollment.student_id == student_id
            for enrollment in self._enrollments.values()
        )
