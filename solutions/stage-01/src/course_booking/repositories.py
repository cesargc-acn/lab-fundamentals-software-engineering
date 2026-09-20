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

    # TODO [stage-2] 1 (core): Declare the three things the service needs from a
    #     course store. Every body is a literal `...`: a protocol says what can be
    #     asked, never how it is answered.
    #     - `def get_by_id(self, course_id: str) -> Optional[Course]:`
    #     - `def list_available_courses(self) -> List[Course]:`
    #     - `def save(self, course: Course) -> None:`
    pass


class EnrollmentRepository(Protocol):
    """Where enrollments are kept."""

    # TODO [stage-2] 2 (core): Two methods this time, same treatment:
    #     - `def save(self, enrollment: Enrollment) -> None:`
    #     - `def exists_for(self, course_id: str, student_id: str) -> bool:`
    #     The second one answers a yes/no question, so it returns a `bool` rather than
    #     an object the caller has to inspect.
    pass


class InMemoryCourseRepository:
    """A dict pretending to be a database. Good enough for a lab and for tests."""

    def __init__(self, courses: Optional[Iterable[Course]] = None) -> None:
        # TODO [stage-2] 3 (core): Keep the courses somewhere. A dict keyed by course
        #     id is enough, and it makes `get_by_id` a one-liner. The optional
        #     `courses` argument is the starting contents: save each one, so that
        #     arriving through the constructor and arriving through `save` cannot end
        #     up meaning different things.
        raise NotImplementedError("TODO [stage-2] 3")

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        # TODO [stage-2] 3 (core): Answer `None` for an id you do not know: do not
        #     raise, and do not invent an empty `Course`. Deciding what a missing
        #     course means is the caller's job.
        #     Otherwise return a copy, not the stored object.
        #     `dataclasses.replace(course)` is imported for exactly this. A caller
        #     that changes what it got back must not change what is stored until it
        #     calls `save`, which is how a real database behaves.
        raise NotImplementedError("TODO [stage-2] 3")

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join, ordered by id."""
        # TODO [stage-2] 3 (core): A course is joinable when it is free, or when it
        #     still has a seat left. Two details the tests check:
        #     - the list comes back sorted by course id;
        #     - these are copies too.
        raise NotImplementedError("TODO [stage-2] 3")

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        # TODO [stage-2] 3 (core): Store a copy under the course id. Same id, same
        #     slot: saving twice must not create two courses, it must replace the
        #     first one.
        raise NotImplementedError("TODO [stage-2] 3")


class InMemoryEnrollmentRepository:
    """The same trick for enrollments."""

    def __init__(self) -> None:
        # TODO [stage-2] 3 (core): A dict keyed by enrollment id. Nothing else to
        #     decide here.
        raise NotImplementedError("TODO [stage-2] 3")

    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        # TODO [stage-2] 3 (core): One line, keyed by `enrollment.enrollment_id`.
        #     `Enrollment` is a frozen dataclass, so nobody can change it behind your
        #     back and there is nothing to copy here.
        raise NotImplementedError("TODO [stage-2] 3")

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        # TODO [stage-2] 3 (core): Return True when some stored enrollment matches
        #     both ids, and False otherwise. Both, not either: the same student on
        #     another course is a different enrollment.
        raise NotImplementedError("TODO [stage-2] 3")
