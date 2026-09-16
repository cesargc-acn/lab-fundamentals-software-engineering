"""Fixtures shared by every stage.

Given. Nothing in this file is an exercise, and you never have to change it.
"""

from __future__ import annotations

import copy

import pytest

from course_booking import legacy_booking
from course_booking.domain.models import Course, Instructor, Student
from course_booking.notifications import FakeNotificationSender
from course_booking.repositories import (
    InMemoryCourseRepository,
    InMemoryEnrollmentRepository,
)

# The rules the legacy code enforces, written down once.
#
#   (course type, capacity, students already enrolled, has payment method, allowed)
#
# tests/test_stage0_characterization.py checks that legacy_booking behaves like
# this table, and tests/test_stage1_policies.py checks that your policies reach
# the same answers. One table, two readers: they cannot drift apart.
LEGACY_DECISIONS = [
    ("free", 2, 0, False, True),
    ("free", 2, 2, False, True),
    ("limited", 2, 0, False, True),
    ("limited", 2, 1, False, True),
    ("limited", 2, 2, False, False),
    ("paid", 3, 0, False, False),
    ("paid", 3, 0, True, True),
    ("paid", 3, 3, True, False),
]


@pytest.fixture(scope="session")
def _pristine_legacy_state():
    """The data legacy_booking is born with, captured before any test runs."""
    return (
        copy.deepcopy(legacy_booking.COURSES),
        copy.deepcopy(legacy_booking.ENROLLMENTS),
        copy.deepcopy(legacy_booking.SENT_EMAILS),
    )


@pytest.fixture(autouse=True)
def reset_legacy_state(_pristine_legacy_state):
    """Put legacy_booking back the way it was before every single test.

    It keeps everything in module-level dictionaries, so without this fixture
    one test decides what the next one sees. Needing this at all is the first
    argument in favour of a repository.
    """
    courses, enrollments, emails = _pristine_legacy_state
    legacy_booking.COURSES.clear()
    legacy_booking.COURSES.update(copy.deepcopy(courses))
    legacy_booking.ENROLLMENTS.clear()
    legacy_booking.ENROLLMENTS.update(copy.deepcopy(enrollments))
    legacy_booking.SENT_EMAILS[:] = copy.deepcopy(emails)
    yield


@pytest.fixture
def sample_instructor() -> Instructor:
    return Instructor(
        instructor_id="i-1", name="Grace Hopper", email="grace@example.com"
    )


@pytest.fixture
def sample_course(sample_instructor: Instructor) -> Course:
    return Course(
        course_id="python-basics",
        title="Python Basics",
        course_type="free",
        capacity=2,
        price=0.0,
        instructor=sample_instructor,
    )


@pytest.fixture
def sample_student() -> Student:
    return Student(
        student_id="s-1",
        name="Ada Lovelace",
        email="ada@example.com",
        has_payment_method=False,
    )


@pytest.fixture
def in_memory_repositories():
    """A fresh, empty (course repository, enrollment repository) pair."""
    return InMemoryCourseRepository(), InMemoryEnrollmentRepository()


@pytest.fixture
def fake_notifier() -> FakeNotificationSender:
    """A notifier that records instead of sending."""
    return FakeNotificationSender()


@pytest.fixture
def client(fake_notifier: FakeNotificationSender):
    """A TestClient talking to the app, wired to empty in-memory repositories.

    The repositories are swapped in through `app.dependency_overrides`, which is
    only possible because the routes ask for them with `Depends`. That is the
    stage 4 lesson, used against itself.
    """
    from fastapi.testclient import TestClient

    from course_booking.api import dependencies
    from course_booking.main import app

    courses = InMemoryCourseRepository()
    enrollments = InMemoryEnrollmentRepository()
    app.dependency_overrides[dependencies.get_course_repository] = lambda: courses
    app.dependency_overrides[dependencies.get_enrollment_repository] = lambda: enrollments
    app.dependency_overrides[dependencies.get_notification_sender] = lambda: fake_notifier
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
