"""Stage 0. What the legacy code does today.

These tests are green before you write anything, and they stay green for the
rest of the workshop. That is the whole point: the problem with
`legacy_booking.py` is not that it is broken.

A characterization test does not say what the code *should* do. It writes down
what it *does*, so that you notice the day it stops doing it.
"""

from __future__ import annotations

import pytest

from conftest import LEGACY_DECISIONS
from course_booking import legacy_booking

pytestmark = pytest.mark.stage0


def test_enrolling_on_a_free_course_returns_a_confirmation():
    result = legacy_booking.enroll_student("python-basics", "s-1", "ada@example.com")

    assert isinstance(result, dict), (
        "A successful enrollment answers with an untyped dict. Nothing tells "
        "the caller which keys it contains: that is one of the things stage 3 "
        "fixes."
    )
    assert result["course_id"] == "python-basics"
    assert result["student_id"] == "s-1"
    assert result["status"] == "confirmed"
    assert result["seats_taken"] == 1


def test_a_successful_enrollment_sends_exactly_one_email():
    legacy_booking.enroll_student("python-basics", "s-1", "ada@example.com")

    assert len(legacy_booking.SENT_EMAILS) == 1
    assert legacy_booking.SENT_EMAILS[0]["to"] == "ada@example.com"
    assert "Python Basics" in legacy_booking.SENT_EMAILS[0]["subject"]


def test_an_unknown_course_answers_none():
    result = legacy_booking.enroll_student("no-such-course", "s-1", "ada@example.com")

    assert result is None, (
        "An unknown course answers None. Remember this: two lines below, a "
        "refused enrollment answers False instead, and the caller has no way "
        "to tell either of them from a bug."
    )


def test_a_malformed_email_answers_none():
    assert legacy_booking.enroll_student("python-basics", "s-1", "not-an-email") is None


def test_an_empty_student_id_answers_none():
    assert legacy_booking.enroll_student("python-basics", "", "ada@example.com") is None


def test_enrolling_twice_answers_false():
    legacy_booking.enroll_student("python-basics", "s-1", "ada@example.com")

    second = legacy_booking.enroll_student("python-basics", "s-1", "ada@example.com")

    assert second is False
    assert len(legacy_booking.SENT_EMAILS) == 1, (
        "A refused enrollment must not send a second email."
    )


def test_a_full_limited_course_answers_false():
    legacy_booking.enroll_student("testing-101", "s-1", "ada@example.com")
    legacy_booking.enroll_student("testing-101", "s-2", "alan@example.com")

    third = legacy_booking.enroll_student("testing-101", "s-3", "edsger@example.com")

    assert third is False


def test_a_free_course_ignores_its_own_capacity():
    for number in range(4):
        result = legacy_booking.enroll_student(
            "python-basics", "s-%d" % number, "s%d@example.com" % number
        )
        assert isinstance(result, dict)

    assert legacy_booking.COURSES["python-basics"]["capacity"] == 2, (
        "The free course has two seats and four students on it. That is not a "
        "bug you have to fix, it is behaviour you have to preserve."
    )


def test_a_paid_course_refuses_a_student_without_a_payment_method():
    result = legacy_booking.enroll_student(
        "architecture-in-practice", "s-1", "ada@example.com", has_payment_method=False
    )

    assert result is False


def test_a_paid_course_accepts_a_student_with_a_payment_method():
    result = legacy_booking.enroll_student(
        "architecture-in-practice", "s-1", "ada@example.com", has_payment_method=True
    )

    assert isinstance(result, dict)
    assert result["price"] == 149.0


@pytest.mark.parametrize(
    "course_type,capacity,already_enrolled,has_payment_method,allowed", LEGACY_DECISIONS
)
def test_the_decision_table(
    course_type, capacity, already_enrolled, has_payment_method, allowed
):
    """The eight cases stage 1 has to reproduce with policies instead of ifs."""
    legacy_booking.COURSES["probe"] = {
        "title": "Probe",
        "type": course_type,
        "capacity": capacity,
        "price": 0.0,
        "students": ["other-%d" % number for number in range(already_enrolled)],
    }

    result = legacy_booking.enroll_student(
        "probe", "s-new", "new@example.com", has_payment_method
    )

    assert isinstance(result, dict) is allowed, (
        "A %r course with %d of %d seats taken, student %s a payment method: "
        "the legacy code says %s."
        % (
            course_type,
            already_enrolled,
            capacity,
            "with" if has_payment_method else "without",
            "yes" if allowed else "no",
        )
    )
