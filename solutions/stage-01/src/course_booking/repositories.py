"""Where the data lives, described as what the service needs to ask for.

The two protocols are the interesting part. They are written from the point of
view of the caller: the service says "give me the course with this id", not
"run this query". Everything below them is one possible answer.
"""

from __future__ import annotations

from dataclasses import replace
from typing import Dict, Iterable, List, Optional, Protocol

from .domain.models import Course, Enrollment


class CourseRepository(Protocol):
    """Where courses are kept."""

    # TODO [stage-2] 1 (core): Declare the three things the service needs from a
    #     course store: `get_by_id(course_id)` returning a `Course` or `None`,
    #     `list_available_courses()` returning a list of courses, and `save(course)`
    #     returning nothing. Bodies are `...`: a protocol says what can be asked,
    #     never how it is answered.
    pass


class EnrollmentRepository(Protocol):
    """Where enrollments are kept."""

    # TODO [stage-2] 2 (core): Two methods this time: `save(enrollment)`, and
    #     `exists_for(course_id, student_id)`. The second one answers a yes/no
    #     question, so it returns a `bool` rather than an object the caller has to
    #     inspect.
    pass


class InMemoryCourseRepository:
    """A dict pretending to be a database. Good enough for a lab and for tests."""

    def __init__(self, courses: Optional[Iterable[Course]] = None) -> None:
        # TODO [stage-2] 3 (core): Keep the courses somewhere. A dict keyed by course
        #     id is enough, and it makes `get_by_id` a one-liner.
        raise NotImplementedError("TODO [stage-2] 3")

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        # TODO [stage-2] 3 (core): Return a copy, not the stored object.
        #     `dataclasses.replace` is imported for that. A caller that mutates what
        #     it got back must not change what is stored until it calls `save`.
        raise NotImplementedError("TODO [stage-2] 3")

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join, ordered by id."""
        # TODO [stage-2] 3 (core): A course is joinable when it is free, or when it
        #     still has a seat left. Copies here too.
        raise NotImplementedError("TODO [stage-2] 3")

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        # TODO [stage-2] 3 (core): Store a copy under the course id. Same id, same
        #     slot: saving twice must not create two courses.
        raise NotImplementedError("TODO [stage-2] 3")


class InMemoryEnrollmentRepository:
    """The same trick for enrollments."""

    def __init__(self) -> None:
        # TODO [stage-2] 3 (core): A dict keyed by enrollment id.
        raise NotImplementedError("TODO [stage-2] 3")

    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        # TODO [stage-2] 3 (core): `Enrollment` is frozen, so there is nothing to copy
        #     here.
        raise NotImplementedError("TODO [stage-2] 3")

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        # TODO [stage-2] 3 (core): Look for an enrollment that matches both ids.
        raise NotImplementedError("TODO [stage-2] 3")
