"""Stage 3. Saying no out loud, and saying what may cross the wire.

Three refusals that used to be indistinguishable now have names, and a caller
can tell them apart without reading the service.
"""

from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from course_booking.domain.errors import (
    CourseNotFoundError,
    DomainError,
    EnrollmentNotAllowedError,
    StudentAlreadyEnrolledError,
)
from course_booking.domain.models import Course, Student
from course_booking.domain.policies import default_enrollment_policy
from course_booking.schemas import CreateEnrollmentRequest, EnrollmentResponse
from course_booking.services.enrollment_service import EnrollmentService

pytestmark = pytest.mark.stage3


def build_service(courses, enrollments, notifier) -> EnrollmentService:
    return EnrollmentService(
        courses=courses,
        enrollments=enrollments,
        policy=default_enrollment_policy(),
        notifier=notifier,
    )


# --- the errors ------------------------------------------------------------

def test_an_unknown_course_raises_course_not_found(
    sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    service = build_service(courses, enrollments, fake_notifier)

    with pytest.raises(CourseNotFoundError) as raised:
        service.enroll_student("no-such-course", sample_student)

    assert raised.value.course_id == "no-such-course", (
        "The error carries the id nobody could find, so a handler can say "
        "which course it was without parsing the message."
    )


def test_enrolling_twice_raises_student_already_enrolled(
    sample_course, sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(sample_course)
    service = build_service(courses, enrollments, fake_notifier)
    service.enroll_student("python-basics", sample_student)

    with pytest.raises(StudentAlreadyEnrolledError) as raised:
        service.enroll_student("python-basics", sample_student)

    assert raised.value.course_id == "python-basics"
    assert raised.value.student_id == "s-1"


def test_a_full_course_raises_enrollment_not_allowed(
    sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(Course("testing-101", "Testing 101", "limited", capacity=1))
    service = build_service(courses, enrollments, fake_notifier)
    service.enroll_student("testing-101", sample_student)

    with pytest.raises(EnrollmentNotAllowedError) as raised:
        service.enroll_student("testing-101", Student("s-2", "Alan", "alan@example.com"))

    assert raised.value.reason, (
        "EnrollmentNotAllowedError carries a reason. The policy answers yes or "
        "no; the service is what knows why the answer was no."
    )


def test_one_except_catches_the_whole_family(
    sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    service = build_service(courses, enrollments, fake_notifier)

    with pytest.raises(DomainError):
        service.enroll_student("no-such-course", sample_student)


def test_a_refusal_no_longer_looks_like_a_result(
    sample_student, in_memory_repositories, fake_notifier
):
    """The point of the stage, in one assertion.

    Before, a caller got None and had to guess. Now nothing comes back at all
    unless the student really is enrolled.
    """
    courses, enrollments = in_memory_repositories
    service = build_service(courses, enrollments, fake_notifier)

    try:
        result = service.enroll_student("no-such-course", sample_student)
    except DomainError:
        return

    pytest.fail(
        "enroll_student answered %r instead of raising. A returned None means "
        "the caller has to check, remember to check, and guess which of the "
        "three failures it was." % (result,)
    )


# --- the log line ----------------------------------------------------------

def test_a_refusal_is_logged_with_structured_fields(
    caplog, sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    service = build_service(courses, enrollments, fake_notifier)

    with caplog.at_level(logging.WARNING):
        with pytest.raises(CourseNotFoundError):
            service.enroll_student("no-such-course", sample_student)

    refusals = [
        record
        for record in caplog.records
        if getattr(record, "operation", None) == "enroll_student"
    ]
    assert refusals, (
        "Nothing was logged. A refusal that leaves no trace is a support "
        "ticket nobody can answer: call _log_failure before you raise."
    )
    record = refusals[0]
    assert record.error_type == "CourseNotFoundError", (
        "The log line says error_type=%r. Whoever reads it at three in the "
        "morning needs to know which failure this was."
        % getattr(record, "error_type", None)
    )
    assert record.levelname == "WARNING"
    assert record.created > 0, "Every record carries the timestamp for free."


# --- the schemas -----------------------------------------------------------

def test_a_valid_enrollment_request_is_accepted():
    request = CreateEnrollmentRequest(
        course_id="python-basics",
        student_id="s-1",
        name="Ada Lovelace",
        email="ada@example.com",
    )

    assert request.course_id == "python-basics"
    assert request.has_payment_method is False, (
        "has_payment_method defaults to False. A client that says nothing has "
        "not said yes."
    )


def test_a_request_without_a_course_id_is_rejected():
    with pytest.raises(ValidationError):
        CreateEnrollmentRequest(
            student_id="s-1", name="Ada Lovelace", email="ada@example.com"
        )


def test_a_request_with_the_wrong_type_is_rejected():
    with pytest.raises(ValidationError):
        CreateEnrollmentRequest(
            course_id="python-basics",
            student_id="s-1",
            name="Ada Lovelace",
            email="ada@example.com",
            has_payment_method="maybe",
        )


def test_an_empty_course_id_is_rejected():
    with pytest.raises(ValidationError):
        CreateEnrollmentRequest(
            course_id="", student_id="s-1", name="Ada", email="ada@example.com"
        )


def test_the_response_carries_the_enrollment_and_not_the_student():
    response = EnrollmentResponse(
        enrollment_id="e-1",
        course_id="python-basics",
        student_id="s-1",
        status="confirmed",
    )

    assert response.status == "confirmed"
    assert not hasattr(response, "email"), (
        "The response model is where you decide what leaves the building. The "
        "student's email address has no reason to."
    )
