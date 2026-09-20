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
        # TODO [stage-2] 4 (core): Store the four collaborators and do nothing else:
        #     no `import` of a concrete repository, no `InMemory...()` call anywhere
        #     in this class. Whoever built the service already decided which
        #     implementations to hand it, and that is the whole point of the exercise.
        #     Keep the four parameter names as they are. The tests build the service
        #     with keyword arguments.
        raise NotImplementedError("TODO [stage-2] 4")

    # TODO [stage-2] 4 (core): Write the enrollment use case, in the order the
    #     whiteboard has it:
    #     - find the course; if there is none, give up;
    #     - refuse a student who already holds a seat on it;
    #     - ask the policy whether this student may enroll;
    #     - build an `Enrollment` (`str(uuid4())` makes a fine id);
    #     - save the enrollment;
    #     - add one to the course's `enrolled_count`, and save the course;
    #     - notify the student, and return the enrollment.
    #     For now signal the three failures the way the legacy code does, by
    #     returning: `None` when the course does not exist, `False` for the other two.
    #     Nothing may happen after a refusal. Stage 3 is where that changes.
    # TODO [stage-3] 2 (core): Replace the three refusal signals with the domain
    #     errors you just wrote, calling `_log_failure` immediately before each
    #     `raise`:
    #     - no such course -> `CourseNotFoundError`;
    #     - the student already holds a seat -> `StudentAlreadyEnrolledError`;
    #     - the policy said no -> `EnrollmentNotAllowedError`, with the sentence
    #       `_rejection_reason(course)` gives you.
    #     The first argument to `_log_failure` is the error type as a string, e.g.
    #     "CourseNotFoundError". Then change the annotation: it can finally say `->
    #     Enrollment` and mean it.
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
