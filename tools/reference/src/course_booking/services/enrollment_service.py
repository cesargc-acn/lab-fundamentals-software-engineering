"""The enrollment use case.

`EnrollmentService` is deliberately synchronous. It waits for nothing: every
call it makes returns immediately, so `async` would buy it exactly nothing and
cost it a keyword on every line. Stage 5 is about the one part of this file
that does wait for something.
"""

from __future__ import annotations

import asyncio
import logging
# @at 0
import time
# @at 5
# @end
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
        # @todo stage=2 id=4 kind=core
        # @text Store the four collaborators and nothing else. No `import` of a
        # @text concrete repository, no `InMemory...()` call here: whoever built
        # @text this service already decided which implementations to hand it,
        # @text and that is the whole point of the exercise.
        # @at 2
        self._courses = courses
        self._enrollments = enrollments
        self._policy = policy
        self._notifier = notifier
        # @end

    # @todo stage=2 id=4 kind=core
    # @text Write the enrollment use case, in the order the whiteboard has it:
    # @text find the course, refuse a student who already has a seat, ask the
    # @text policy, create the `Enrollment`, save it, count the seat on the
    # @text course, save the course, notify the student, return the enrollment.
    # @text For now signal the three failures the way the legacy code does, by
    # @text returning. Stage 3 is where that changes.
    # @todo stage=3 id=2 kind=core
    # @text Replace the three `return None` / `return False` signals with the
    # @text domain errors you just wrote, and call `_log_failure` before each
    # @text one. Then look at the return type: it can finally say `Enrollment`
    # @text and mean it.
    # @at 0
    def enroll_student(
        self, course_id: str, student: Student
    ) -> Union[Enrollment, None, bool]:
        """Enroll `student` on `course_id` and return the enrollment."""
        raise NotImplementedError("TODO [stage-2] 4")
    # @at 2
    def enroll_student(
        self, course_id: str, student: Student
    ) -> Union[Enrollment, None, bool]:
        """Enroll `student` on `course_id` and return the enrollment.

        Read the return type out loud. An `Enrollment`, or `None`, or a `bool`:
        the caller has to guess what happened and why. That is what signalling
        failure with return values costs, and stage 3 is where it is paid back.
        """
        course = self._courses.get_by_id(course_id)
        if course is None:
            return None
        if self._enrollments.exists_for(course_id, student.student_id):
            return False
        if not self._policy.can_enroll(course, student):
            return False

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
    # @at 3
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
    # @end


# ---------------------------------------------------------------------------
# Stage 5. The only code in the project that waits for something.
# ---------------------------------------------------------------------------

async def charge_enrollment(
    gateway: PaymentGateway, student_id: str, amount: float
) -> PaymentResult:
    """Wait for the settlement window to open, then charge the student."""
    # @todo stage=5 id=1 kind=core
    # @text Read the next line the way the event loop reads it. While it waits,
    # @text nothing else in the process runs: not the other four requests, not
    # @text the health check, nothing. `async def` did not make it concurrent.
    # @text There is an awaitable version of that call. Use it.
    # @at 0
    time.sleep(SETTLEMENT_DELAY_SECONDS)
    # @at 5
    await asyncio.sleep(SETTLEMENT_DELAY_SECONDS)
    # @end
    return await gateway.charge(student_id, amount)


async def payment_summary(
    gateway: PaymentGateway, student_id: str, amount: float
) -> str:
    """One line describing the charge, for the API to hand back."""
    # @todo stage=5 id=2 kind=core
    # @text Calling an `async def` gives you a coroutine, not a result, and
    # @text nobody tells you: the line below runs, the string gets built, and
    # @text the payment never happens. The proof shows up in the response body.
    # @at 0
    result = charge_enrollment(gateway, student_id, amount)
    # @at 5
    result = await charge_enrollment(gateway, student_id, amount)
    # @end
    return "payment: %s" % result


async def charge_many(
    gateway: PaymentGateway, charges: Sequence[Tuple[str, float]]
) -> List[PaymentResult]:
    """Charge several students. No charge depends on the one before it."""
    # @todo stage=5 id=3 kind=optional
    # @text These charges have nothing to do with each other, and yet the loop
    # @text below makes each one wait for the last. Start them all, then wait
    # @text once. Nothing tests this one: compare the two versions with a clock.
    # @at 0
    results = []
    for student_id, amount in charges:
        results.append(await charge_enrollment(gateway, student_id, amount))
    return results
    # @at 5
    return list(
        await asyncio.gather(
            *(charge_enrollment(gateway, student_id, amount)
              for student_id, amount in charges)
        )
    )
    # @end
