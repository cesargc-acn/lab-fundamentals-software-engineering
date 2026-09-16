"""The nouns of the domain, as typed dataclasses.

Given: writing these is mechanical and teaches nothing that the enrollment
policy does not teach better. Read them once, then use them.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

COURSE_TYPES = ("free", "limited", "paid")


@dataclass(frozen=True)
class Instructor:
    """Whoever teaches the course."""

    instructor_id: str
    name: str
    email: str


@dataclass(frozen=True)
class Student:
    """Whoever wants a seat."""

    student_id: str
    name: str
    email: str
    has_payment_method: bool = False


@dataclass
class Course:
    """A course, and how full it is right now.

    This one is mutable on purpose: enrolling a student changes
    `enrolled_count`, and the repository is what persists that change.
    """

    course_id: str
    title: str
    course_type: str
    capacity: int
    price: float = 0.0
    enrolled_count: int = 0
    instructor: Optional[Instructor] = None

    @property
    def seats_left(self) -> int:
        return self.capacity - self.enrolled_count


@dataclass(frozen=True)
class Enrollment:
    """The fact that a student holds a seat on a course."""

    enrollment_id: str
    course_id: str
    student_id: str
    status: str = "confirmed"
