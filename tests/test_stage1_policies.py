"""Stage 1. One rule per course type, and no `elif` anywhere.

These tests never ask how you built a policy. They ask what it answers.
"""

from __future__ import annotations

import pytest

from conftest import LEGACY_DECISIONS
from course_booking.domain.models import Course, Student
from course_booking.domain.policies import (
    EnrollmentPolicy,
    FreeEnrollmentPolicy,
    LimitedCapacityPolicy,
    PaidEnrollmentPolicy,
    default_enrollment_policy,
)

pytestmark = pytest.mark.stage1


def course(course_type: str, capacity: int = 2, enrolled_count: int = 0) -> Course:
    return Course(
        course_id="probe",
        title="Probe",
        course_type=course_type,
        capacity=capacity,
        enrolled_count=enrolled_count,
    )


def student(has_payment_method: bool = False) -> Student:
    return Student(
        student_id="s-new",
        name="New Student",
        email="new@example.com",
        has_payment_method=has_payment_method,
    )


def test_the_protocol_declares_can_enroll():
    assert hasattr(EnrollmentPolicy, "can_enroll"), (
        "EnrollmentPolicy does not declare can_enroll yet. A protocol is the "
        "list of questions a caller is allowed to ask; write the declaration in "
        "src/course_booking/domain/policies.py. The body stays as `...`."
    )


@pytest.mark.parametrize("enrolled_count", [0, 1, 2, 7])
def test_a_free_course_always_says_yes(enrolled_count):
    allowed = FreeEnrollmentPolicy().can_enroll(
        course("free", capacity=2, enrolled_count=enrolled_count), student()
    )

    assert allowed is True, (
        "FreeEnrollmentPolicy refused a student on a free course with %d "
        "enrolled. The legacy code does not count seats on free courses, and "
        "neither should this policy." % enrolled_count
    )


@pytest.mark.parametrize(
    "capacity,enrolled_count,expected",
    [(2, 0, True), (2, 1, True), (2, 2, False), (2, 3, False), (0, 0, False)],
)
def test_a_limited_course_counts_seats(capacity, enrolled_count, expected):
    allowed = LimitedCapacityPolicy().can_enroll(
        course("limited", capacity=capacity, enrolled_count=enrolled_count), student()
    )

    assert allowed is expected, (
        "LimitedCapacityPolicy said %s for a course with %d of %d seats taken. "
        "A student gets in while there is a seat left, and not once there is "
        "not." % (allowed, enrolled_count, capacity)
    )


@pytest.mark.parametrize(
    "enrolled_count,has_payment_method,expected",
    [(0, True, True), (0, False, False), (2, True, False), (2, False, False)],
)
def test_a_paid_course_needs_a_seat_and_a_payment_method(
    enrolled_count, has_payment_method, expected
):
    allowed = PaidEnrollmentPolicy().can_enroll(
        course("paid", capacity=2, enrolled_count=enrolled_count),
        student(has_payment_method=has_payment_method),
    )

    assert allowed is expected, (
        "PaidEnrollmentPolicy said %s for a course with %d of 2 seats taken "
        "and a student %s a payment method. Both conditions have to hold."
        % (allowed, enrolled_count, "with" if has_payment_method else "without")
    )


@pytest.mark.parametrize(
    "course_type,capacity,already_enrolled,has_payment_method,allowed", LEGACY_DECISIONS
)
def test_policies_match_legacy_behaviour(
    course_type, capacity, already_enrolled, has_payment_method, allowed
):
    """The same eight cases as test_stage0_characterization, decided by policies.

    This is the test that says the rewrite is faithful. If it is green, your
    four small classes agree with the `if/elif` chain you are replacing on
    every case the old tests pin down.
    """
    policy = default_enrollment_policy()

    decision = policy.can_enroll(
        course(course_type, capacity=capacity, enrolled_count=already_enrolled),
        student(has_payment_method=has_payment_method),
    )

    assert decision is allowed, (
        "The policies disagree with legacy_booking on a %r course with %d of "
        "%d seats taken, student %s a payment method: the old code says %s, "
        "yours says %s."
        % (
            course_type,
            already_enrolled,
            capacity,
            "with" if has_payment_method else "without",
            allowed,
            decision,
        )
    )


def test_an_unknown_course_type_is_refused_rather_than_crashing():
    decision = default_enrollment_policy().can_enroll(course("cooking"), student())

    assert decision is False
