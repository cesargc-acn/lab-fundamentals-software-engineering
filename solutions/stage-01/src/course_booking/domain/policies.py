"""Who may take which course.

One rule per course type, each one small enough to read in a breath. The
service never asks "what type of course is this?"; it asks a policy.
"""

from __future__ import annotations

from typing import Mapping, Protocol

from .models import Course, Student


class EnrollmentPolicy(Protocol):
    """A rule that answers one question: may this student take this course?"""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        ...


class FreeEnrollmentPolicy:
    """Free courses have no gate. Seats are not counted."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        return True


class LimitedCapacityPolicy:
    """Courses with a fixed number of seats."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        return course.enrolled_count < course.capacity


class PaidEnrollmentPolicy:
    """Courses you have to pay for. Seats are counted too."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        return course.enrolled_count < course.capacity and student.has_payment_method


class CourseTypeEnrollmentPolicy:
    """Given. A policy whose job is to pick the policy for a course type.

    It satisfies `EnrollmentPolicy` itself, which is why the service can take a
    single policy and still behave differently for free, limited and paid
    courses. A course type nobody registered is rejected rather than crashing.
    """

    def __init__(self, policies: Mapping[str, EnrollmentPolicy]) -> None:
        self._policies = dict(policies)

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        policy = self._policies.get(course.course_type)
        if policy is None:
            return False
        return policy.can_enroll(course, student)


def default_enrollment_policy() -> EnrollmentPolicy:
    """Given. The policy the application runs with: one per course type."""
    return CourseTypeEnrollmentPolicy(
        {
            "free": FreeEnrollmentPolicy(),
            "limited": LimitedCapacityPolicy(),
            "paid": PaidEnrollmentPolicy(),
        }
    )
