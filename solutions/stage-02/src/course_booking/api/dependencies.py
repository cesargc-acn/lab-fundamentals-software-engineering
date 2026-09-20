"""Who builds what, and how a route gets hold of it.

This file is the composition root: the one place that knows which concrete
class goes behind each protocol. Delete it and the domain still compiles.

Stage 4. Every function here is a "provider": it builds one thing and returns
it. A route never builds anything itself, it asks with `Depends(provider)`, and
FastAPI calls the provider first and passes the result in. That indirection is
what lets `tests/conftest.py` swap the repositories with
`app.dependency_overrides` without a single change to the routes.

Write the providers before the routes, or the routes will have nothing to ask
for.
"""

from __future__ import annotations

from functools import lru_cache

from fastapi import Depends

from ..domain.policies import default_enrollment_policy
from ..notifications import EmailNotificationSender, NotificationSender
from ..payments import PaymentGateway
from ..repositories import (
    CourseRepository,
    EnrollmentRepository,
    InMemoryCourseRepository,
    InMemoryEnrollmentRepository,
)
from ..services.enrollment_service import EnrollmentService


@lru_cache(maxsize=1)
def get_course_repository() -> CourseRepository:
    """The single course repository the whole application shares.

    `lru_cache` is what makes it single: the first request builds it, every
    other request gets the same object back.
    """
    # TODO [stage-4] 3 (core): Return an `InMemoryCourseRepository()`. One line. The
    #     `lru_cache` above is already what makes it shared: the first request builds
    #     it, every request after that gets the same object.
    raise NotImplementedError("TODO [stage-4] 3")


@lru_cache(maxsize=1)
def get_enrollment_repository() -> EnrollmentRepository:
    """The single enrollment repository the whole application shares."""
    # TODO [stage-4] 3 (core): Same again, one line, for
    #     `InMemoryEnrollmentRepository`.
    raise NotImplementedError("TODO [stage-4] 3")


def get_notification_sender() -> NotificationSender:
    """The sender the application notifies with."""
    # TODO [stage-4] 3 (core): Return an `EmailNotificationSender()`. No `lru_cache`
    #     on this one: it holds no state worth sharing.
    #     If you wrote `create_notification_sender` back in stage 2, call it with
    #     "email" instead. This is exactly the caller it was written for.
    raise NotImplementedError("TODO [stage-4] 3")


@lru_cache(maxsize=1)
def get_payment_gateway() -> PaymentGateway:
    """Given. Stage 5 needs it; nothing before stage 5 does."""
    return PaymentGateway()


def get_enrollment_service(
    courses: CourseRepository = Depends(get_course_repository),
    enrollments: EnrollmentRepository = Depends(get_enrollment_repository),
    notifier: NotificationSender = Depends(get_notification_sender),
) -> EnrollmentService:
    """Build the service for one request out of the dependencies above."""
    # TODO [stage-4] 3 (core): Build and return the `EnrollmentService` with its four
    #     collaborators. Three of them are already sitting in the parameters above,
    #     because `Depends` resolved them before this function ran; the fourth, the
    #     policy, comes from `default_enrollment_policy()`.
    #     Do not call the other providers by hand here. Asking through `Depends` is
    #     what lets a test override one of them and have the service built one layer
    #     up pick the override up.
    raise NotImplementedError("TODO [stage-4] 3")
