"""The enrollment use case.

`EnrollmentService` is deliberately synchronous. It waits for nothing: every
call it makes returns immediately, so `async` would buy it exactly nothing and
cost it a keyword on every line. Stage 5 is about the one part of this file
that does wait for something.

Three stages touch this file, in this order:

    stage 2   build the service and write `enroll_student`
    stage 3   turn its three silent refusals into raised domain errors
    stage 5   fix the two async bugs below the banner at the bottom

`_rejection_reason` and `_log_failure` are given. You call them; you do not
write them.
"""

from __future__ import annotations

import asyncio
import logging
import time
from typing import List, Sequence, Tuple, Union
from uuid import uuid4

from ..domain.errors import (
    CourseNotFoundError,
    EnrollmentNotAllowedError,
    StudentAlreadyEnrolledError,
)
from ..domain.models import Course, Enrollment, Student
from ..domain.policies import EnrollmentPolicy
from ..notifications import NotificationSender
from ..payments import PaymentGateway, PaymentResult
from ..repositories import CourseRepository, EnrollmentRepository

logger = logging.getLogger(__name__)

SETTLEMENT_DELAY_SECONDS = 0.3


def _rejection_reason(course: Course) -> str:
    """Given. The policy answers yes or no; this turns a no into a sentence."""
    if course.course_type == "paid":
        return "the course is full, or the student has no payment method"
    if course.course_type == "limited":
        return "the course is full"
    return "the enrollment policy for a %r course refused it" % course.course_type


def _log_failure(error_type: str, course_id: str, student_id: str) -> None:
    """Given. One structured log line per refusal.

    `operation` and `error_type` are the fields this project adds; the record
    already carries the timestamp and the level, so there is no point repeating
    them here.
    """
    logger.warning(
        "enrollment refused",
        extra={
            "operation": "enroll_student",
            "error_type": error_type,
            "course_id": course_id,
            "student_id": student_id,
        },
    )


class EnrollmentService:
    """Puts a student on a course, or explains why it will not."""

    def __init__(
        self,
        courses: CourseRepository,
        enrollments: EnrollmentRepository,
        policy: EnrollmentPolicy,
        notifier: NotificationSender,
    ) -> None:
        self._courses = courses
        self._enrollments = enrollments
        self._policy = policy
        self._notifier = notifier

    def enroll_student(self, course_id: str, student: Student) -> Enrollment:
        """Enroll `student` on `course_id` and return the enrollment.

        Raises `CourseNotFoundError`, `StudentAlreadyEnrolledError` or
        `EnrollmentNotAllowedError`. The return type is now the truth: if this
        call comes back, the student is in.
        """
        course = self._courses.get_by_id(course_id)
        if course is None:
            _log_failure("CourseNotFoundError", course_id, student.student_id)
            raise CourseNotFoundError(course_id)
        if self._enrollments.exists_for(course_id, student.student_id):
            _log_failure("StudentAlreadyEnrolledError", course_id, student.student_id)
            raise StudentAlreadyEnrolledError(course_id, student.student_id)
        if not self._policy.can_enroll(course, student):
            reason = _rejection_reason(course)
            _log_failure("EnrollmentNotAllowedError", course_id, student.student_id)
            raise EnrollmentNotAllowedError(course_id, student.student_id, reason)

        enrollment = Enrollment(
            enrollment_id=str(uuid4()),
            course_id=course_id,
            student_id=student.student_id,
        )
        self._enrollments.save(enrollment)
        course.enrolled_count += 1
        self._courses.save(course)
        self._notifier.notify_enrollment(course, student)
        return enrollment


# ---------------------------------------------------------------------------
# Stage 5. The only code in the project that waits for something.
# ---------------------------------------------------------------------------

async def charge_enrollment(
    gateway: PaymentGateway, student_id: str, amount: float
) -> PaymentResult:
    """Wait for the settlement window to open, then charge the student."""
    # TODO [stage-5] 1 (core): Read the next line the way the event loop reads it.
    #     While it waits, nothing else in the process runs: not the other four
    #     charges, not the health check, nothing. `async def` did not make this
    #     concurrent and never could: only handing control back does that, and
    #     `time.sleep` never hands anything back.
    #     There is an awaitable version of that call in `asyncio`. Swap it in. The
    #     delay still has to happen, and the charge on the line after it still has to
    #     reach the gateway.
    time.sleep(SETTLEMENT_DELAY_SECONDS)
    return await gateway.charge(student_id, amount)


async def payment_summary(
    gateway: PaymentGateway, student_id: str, amount: float
) -> str:
    """One line describing the charge, for the API to hand back."""
    # TODO [stage-5] 2 (core): `charge_enrollment` is an `async def`, so the line
    #     below hands you a coroutine object, not a result, and Python does not
    #     complain. The string still gets built, the API still answers 200, and nobody
    #     was ever charged. One keyword fixes it.
    #     Before you fix it, run the server and call `POST /enrollments/payment` from
    #     /docs: seeing `payment: <coroutine object ...>` go out over HTTP is the
    #     point of this task.
    result = charge_enrollment(gateway, student_id, amount)
    return "payment: %s" % result


async def charge_many(
    gateway: PaymentGateway, charges: Sequence[Tuple[str, float]]
) -> List[PaymentResult]:
    """Charge several students. No charge depends on the one before it."""
    # TODO [stage-5] 3 (optional): These charges have nothing to do with each other,
    #     and yet the loop below makes each one wait for the last. Start them all,
    #     then wait once: `asyncio.gather` is the usual way.
    #     Nothing tests this one. Time the two versions yourself with
    #     `time.perf_counter` and a list of five charges.
    results = []
    for student_id, amount in charges:
        results.append(await charge_enrollment(gateway, student_id, amount))
    return results
