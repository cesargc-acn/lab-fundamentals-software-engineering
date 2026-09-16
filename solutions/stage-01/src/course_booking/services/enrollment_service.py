"""The enrollment use case.

`EnrollmentService` is deliberately synchronous. It waits for nothing: every
call it makes returns immediately, so `async` would buy it exactly nothing and
cost it a keyword on every line. Stage 5 is about the one part of this file
that does wait for something.
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
        # TODO [stage-2] 4 (core): Store the four collaborators and nothing else. No
        #     `import` of a concrete repository, no `InMemory...()` call here: whoever
        #     built this service already decided which implementations to hand it, and
        #     that is the whole point of the exercise.
        raise NotImplementedError("TODO [stage-2] 4")

    # TODO [stage-2] 4 (core): Write the enrollment use case, in the order the
    #     whiteboard has it: find the course, refuse a student who already has a seat,
    #     ask the policy, create the `Enrollment`, save it, count the seat on the
    #     course, save the course, notify the student, return the enrollment. For now
    #     signal the three failures the way the legacy code does, by returning. Stage
    #     3 is where that changes.
    # TODO [stage-3] 2 (core): Replace the three `return None` / `return False`
    #     signals with the domain errors you just wrote, and call `_log_failure`
    #     before each one. Then look at the return type: it can finally say
    #     `Enrollment` and mean it.
    def enroll_student(
        self, course_id: str, student: Student
    ) -> Union[Enrollment, None, bool]:
        """Enroll `student` on `course_id` and return the enrollment."""
        raise NotImplementedError("TODO [stage-2] 4")


# ---------------------------------------------------------------------------
# Stage 5. The only code in the project that waits for something.
# ---------------------------------------------------------------------------

async def charge_enrollment(
    gateway: PaymentGateway, student_id: str, amount: float
) -> PaymentResult:
    """Wait for the settlement window to open, then charge the student."""
    # TODO [stage-5] 1 (core): Read the next line the way the event loop reads it.
    #     While it waits, nothing else in the process runs: not the other four
    #     requests, not the health check, nothing. `async def` did not make it
    #     concurrent. There is an awaitable version of that call. Use it.
    time.sleep(SETTLEMENT_DELAY_SECONDS)
    return await gateway.charge(student_id, amount)


async def payment_summary(
    gateway: PaymentGateway, student_id: str, amount: float
) -> str:
    """One line describing the charge, for the API to hand back."""
    # TODO [stage-5] 2 (core): Calling an `async def` gives you a coroutine, not a
    #     result, and nobody tells you: the line below runs, the string gets built,
    #     and the payment never happens. The proof shows up in the response body.
    result = charge_enrollment(gateway, student_id, amount)
    return "payment: %s" % result


async def charge_many(
    gateway: PaymentGateway, charges: Sequence[Tuple[str, float]]
) -> List[PaymentResult]:
    """Charge several students. No charge depends on the one before it."""
    # TODO [stage-5] 3 (optional): These charges have nothing to do with each other,
    #     and yet the loop below makes each one wait for the last. Start them all,
    #     then wait once. Nothing tests this one: compare the two versions with a
    #     clock.
    results = []
    for student_id, amount in charges:
        results.append(await charge_enrollment(gateway, student_id, amount))
    return results
