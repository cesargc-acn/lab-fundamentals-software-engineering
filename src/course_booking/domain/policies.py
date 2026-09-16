"""Who may take which course.

One rule per course type, each one small enough to read in a breath. The
service never asks "what type of course is this?"; it asks a policy.
"""

from __future__ import annotations

from typing import Mapping, Protocol

from .models import Course, Student


class EnrollmentPolicy(Protocol):
    """A rule that answers one question: may this student take this course?"""

    # TODO [stage-1] 1 (core): Declare the one method of the protocol: `can_enroll`,
    #     taking a `Course` and a `Student` and returning a `bool`. A protocol method
    #     has no implementation, so its body is a literal `...`. Nothing has to
    #     inherit from this class: any object with a matching `can_enroll` already
    #     satisfies it.
    pass


class FreeEnrollmentPolicy:
    """Free courses have no gate. Seats are not counted."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # TODO [stage-1] 2 (core): Read what `legacy_booking.enroll_student` does when
        #     the course type is "free" and say the same thing in one line.
        raise NotImplementedError("TODO [stage-1] 2")


class LimitedCapacityPolicy:
    """Courses with a fixed number of seats."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # TODO [stage-1] 3 (core): Compare how many students are already enrolled with
        #     the number of seats. `Course` carries both numbers, and a `seats_left`
        #     property if you prefer it.
        raise NotImplementedError("TODO [stage-1] 3")


class PaidEnrollmentPolicy:
    """Courses you have to pay for. Seats are counted too."""

    def can_enroll(self, course: Course, student: Student) -> bool:
        """Return True when `student` may take `course`."""
        # TODO [stage-1] 4 (core): A paid course asks two questions, not one: is there
        #     a seat left, and does the student have a payment method? Both have to be
        #     true. Check `legacy_booking` if you are unsure of the order.
        raise NotImplementedError("TODO [stage-1] 4")


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
