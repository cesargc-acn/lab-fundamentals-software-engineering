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
    return InMemoryCourseRepository()


@lru_cache(maxsize=1)
def get_enrollment_repository() -> EnrollmentRepository:
    """The single enrollment repository the whole application shares."""
    return InMemoryEnrollmentRepository()


def get_notification_sender() -> NotificationSender:
    """The sender the application notifies with."""
    return EmailNotificationSender()


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
    return EnrollmentService(
        courses=courses,
        enrollments=enrollments,
        policy=default_enrollment_policy(),
        notifier=notifier,
    )
