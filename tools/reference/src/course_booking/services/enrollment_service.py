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
        # @text Store the four collaborators and do nothing else: no `import`
        # @text of a concrete repository, no `InMemory...()` call anywhere in
        # @text this class. Whoever built the service already decided which
        # @text implementations to hand it, and that is the whole point of the
        # @text exercise.
        # @text | Keep the four parameter names as they are. The tests build
        # @text the service with keyword arguments.
        # @at 2
        self._courses = courses
        self._enrollments = enrollments
        self._policy = policy
        self._notifier = notifier
        # @end

    # @todo stage=2 id=4 kind=core
    # @text Write the enrollment use case, in the order the whiteboard has it:
    # @text - find the course; if there is none, give up;
    # @text - refuse a student who already holds a seat on it;
    # @text - ask the policy whether this student may enroll;
    # @text - build an `Enrollment` (`str(uuid4())` makes a fine id);
    # @text - save the enrollment;
    # @text - add one to the course's `enrolled_count`, and save the course;
    # @text - notify the student, and return the enrollment.
    # @text | For now signal the three failures the way the legacy code does,
    # @text by returning: `None` when the course does not exist, `False` for
    # @text the other two. Nothing may happen after a refusal. Stage 3 is where
    # @text that changes.
    # @todo stage=3 id=2 kind=core
    # @text Replace the three refusal signals with the domain errors you just
    # @text wrote, calling `_log_failure` immediately before each `raise`:
    # @text - no such course -> `CourseNotFoundError`;
    # @text - the student already holds a seat -> `StudentAlreadyEnrolledError`;
    # @text - the policy said no -> `EnrollmentNotAllowedError`, with the
    # @text sentence `_rejection_reason(course)` gives you.
    # @text | The first argument to `_log_failure` is the error type as a
    # @text string, e.g. "CourseNotFoundError". Then change the annotation: it
    # @text can finally say `-> Enrollment` and mean it.
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
    # @text nothing else in the process runs: not the other four charges, not
    # @text the health check, nothing. `async def` did not make this concurrent
    # @text and never could: only handing control back does that, and
    # @text `time.sleep` never hands anything back.
    # @text | There is an awaitable version of that call in `asyncio`. Swap it
    # @text in. The delay still has to happen, and the charge on the line after
    # @text it still has to reach the gateway.
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
    # @text `charge_enrollment` is an `async def`, so the line below hands you
    # @text a coroutine object, not a result, and Python does not complain. The
    # @text string still gets built, the API still answers 200, and nobody was
    # @text ever charged. One keyword fixes it.
    # @text | Before you fix it, run the server and call
    # @text `POST /enrollments/payment` from /docs: seeing `payment: <coroutine
    # @text object ...>` go out over HTTP is the point of this task.
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
    # @text once: `asyncio.gather` is the usual way.
    # @text | Nothing tests this one. Time the two versions yourself with
    # @text `time.perf_counter` and a list of five charges.
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
