"""Who may take which course.

One rule per course type, each one small enough to read in a breath. The
service never asks "what type of course is this?"; it asks a policy.

Stage 1 happens here. You write one protocol and three tiny classes; the two
classes at the bottom of the file are given and need no changes. The rules you
are copying are in `legacy_booking.enroll_student`, and the eight cases they
have to agree on are the `LEGACY_DECISIONS` table in `tests/conftest.py`.
"""

from __future__ import annotations

from typing import Mapping, Protocol

from .models import Course, Student


class EnrollmentPolicy(Protocol):
    """A rule that answers one question: may this student take this course?"""

    # @todo stage=1 id=1 kind=core
    # @text Declare the one method of this protocol, exactly like this, with a
    # @text literal `...` as the whole body:
    # @text - `def can_enroll(self, course: Course, student: Student) -> bool:`
    # @text | A protocol lists what a caller may ask for and implements none of
    # @text it. Nothing has to inherit from this class: any object with a
    # @text matching `can_enroll` already satisfies it.
    # @stub pass
    # @at 1
    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        ...
    # @end


class FreeEnrollmentPolicy:
    """Free courses have no gate. Seats are not counted."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # @todo stage=1 id=2 kind=core
        # @text Read what `legacy_booking.enroll_student` does when the course
        # @text type is "free", and say the same thing in one line. It does not
        # @text count seats there, so neither do you. Return a real `bool`: the
        # @text test compares with `is True`.
        # @at 1
        return True
        # @end


class LimitedCapacityPolicy:
    """Courses with a fixed number of seats."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # @todo stage=1 id=3 kind=core
        # @text Return True while there is a seat left and False once there is
        # @text not. `Course` carries `enrolled_count` and `capacity`, and a
        # @text `seats_left` property if you prefer reading it that way. Mind
        # @text the boundary: 2 of 2 seats taken means full.
        # @at 1
        return course.enrolled_count < course.capacity
        # @end


class PaidEnrollmentPolicy:
    """Courses you have to pay for. Seats are counted too."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # @todo stage=1 id=4 kind=core
        # @text A paid course asks two questions, not one, and both have to be
        # @text true:
        # @text - is there a seat left, as in the policy above?
        # @text - does the student have one? `Student.has_payment_method`.
        # @text | Check `legacy_booking` if you are unsure of the order.
        # @at 1
        return course.enrolled_count < course.capacity and student.has_payment_method
        # @end


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
