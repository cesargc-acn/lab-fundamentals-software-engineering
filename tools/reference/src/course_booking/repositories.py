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

    # @todo stage=2 id=1 kind=core
    # @text Declare the three things the service needs from a course store.
    # @text Every body is a literal `...`: a protocol says what can be asked,
    # @text never how it is answered.
    # @text - `def get_by_id(self, course_id: str) -> Optional[Course]:`
    # @text - `def list_available_courses(self) -> List[Course]:`
    # @text - `def save(self, course: Course) -> None:`
    # @stub pass
    # @at 2
    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        ...

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join."""
        ...

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        ...
    # @end


class EnrollmentRepository(Protocol):
    """Where enrollments are kept."""

    # @todo stage=2 id=2 kind=core
    # @text Two methods this time, same treatment:
    # @text - `def save(self, enrollment: Enrollment) -> None:`
    # @text - `def exists_for(self, course_id: str, student_id: str) -> bool:`
    # @text | The second one answers a yes/no question, so it returns a `bool`
    # @text rather than an object the caller has to inspect.
    # @stub pass
    # @at 2
    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        ...

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        ...
    # @end


class InMemoryCourseRepository:
    """A dict pretending to be a database. Good enough for a lab and for tests."""

    def __init__(self, courses: Optional[Iterable[Course]] = None) -> None:
        # @todo stage=2 id=3 kind=core
        # @text Keep the courses somewhere. A dict keyed by course id is
        # @text enough, and it makes `get_by_id` a one-liner. The optional
        # @text `courses` argument is the starting contents: save each one, so
        # @text that arriving through the constructor and arriving through
        # @text `save` cannot end up meaning different things.
        # @at 2
        self._courses: Dict[str, Course] = {}
        for course in courses or ():
            self.save(course)
        # @end

    def get_by_id(self, course_id: str) -> Optional[Course]:
        """Return the course with that id, or None when there is none."""
        # @todo stage=2 id=3 kind=core
        # @text Answer `None` for an id you do not know: do not raise, and do
        # @text not invent an empty `Course`. Deciding what a missing course
        # @text means is the caller's job.
        # @text | Otherwise return a copy, not the stored object.
        # @text `dataclasses.replace(course)` is imported for exactly this. A
        # @text caller that changes what it got back must not change what is
        # @text stored until it calls `save`, which is how a real database
        # @text behaves.
        # @at 2
        stored = self._courses.get(course_id)
        return replace(stored) if stored is not None else None
        # @end

    def list_available_courses(self) -> List[Course]:
        """Return the courses a student could still join, ordered by id."""
        # @todo stage=2 id=3 kind=core
        # @text A course is joinable when it is free, or when it still has a
        # @text seat left. Two details the tests check:
        # @text - the list comes back sorted by course id;
        # @text - these are copies too.
        # @at 2
        return [
            replace(course)
            for course in sorted(self._courses.values(), key=lambda c: c.course_id)
            if course.course_type == "free" or course.seats_left > 0
        ]
        # @end

    def save(self, course: Course) -> None:
        """Insert `course`, or replace the one stored under the same id."""
        # @todo stage=2 id=3 kind=core
        # @text Store a copy under the course id. Same id, same slot: saving
        # @text twice must not create two courses, it must replace the first
        # @text one.
        # @at 2
        self._courses[course.course_id] = replace(course)
        # @end


class InMemoryEnrollmentRepository:
    """The same trick for enrollments."""

    def __init__(self) -> None:
        # @todo stage=2 id=3 kind=core
        # @text A dict keyed by enrollment id. Nothing else to decide here.
        # @at 2
        self._enrollments: Dict[str, Enrollment] = {}
        # @end

    def save(self, enrollment: Enrollment) -> None:
        """Insert `enrollment`, or replace the one stored under the same id."""
        # @todo stage=2 id=3 kind=core
        # @text One line, keyed by `enrollment.enrollment_id`. `Enrollment` is
        # @text a frozen dataclass, so nobody can change it behind your back
        # @text and there is nothing to copy here.
        # @at 2
        self._enrollments[enrollment.enrollment_id] = enrollment
        # @end

    def exists_for(self, course_id: str, student_id: str) -> bool:
        """Return True when that student already holds a seat on that course."""
        # @todo stage=2 id=3 kind=core
        # @text Return True when some stored enrollment matches both ids, and
        # @text False otherwise. Both, not either: the same student on another
        # @text course is a different enrollment.
        # @at 2
        return any(
            enrollment.course_id == course_id and enrollment.student_id == student_id
            for enrollment in self._enrollments.values()
        )
        # @end
