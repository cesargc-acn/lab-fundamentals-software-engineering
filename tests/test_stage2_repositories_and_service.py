"""Stage 2. Somewhere to keep things, and a service that is handed its tools.

Nothing here looks inside a repository or a service. The tests only use what
the protocols promise, which is exactly why the swap test at the bottom can
work at all.
"""

from __future__ import annotations

from typing import Iterable, List, Optional

import pytest

from course_booking.domain.errors import DomainError
from course_booking.domain.models import Course, Enrollment, Student
from course_booking.domain.policies import default_enrollment_policy
from course_booking.repositories import (
    InMemoryCourseRepository,
    InMemoryEnrollmentRepository,
)
from course_booking.services.enrollment_service import EnrollmentService

pytestmark = pytest.mark.stage2


def attempt(service: EnrollmentService, course_id: str, student: Student):
    """Try to enroll, and swallow a refusal however it is signalled.

    At this stage the service says no by returning something falsy; from stage 3
    it says no by raising. These tests do not care which: they check that the
    seat was not taken, not how the bad news travelled.
    """
    try:
        return service.enroll_student(course_id, student)
    except DomainError:
        return None


def build_service(courses, enrollments, notifier) -> EnrollmentService:
    return EnrollmentService(
        courses=courses,
        enrollments=enrollments,
        policy=default_enrollment_policy(),
        notifier=notifier,
    )


class ListCourseRepository:
    """A second, equally valid CourseRepository, backed by a list.

    It is here to be swapped in for InMemoryCourseRepository at the bottom of
    this file. If the service notices the difference, something in it knows
    more about storage than it should.
    """

    def __init__(self, courses: Iterable[Course] = ()) -> None:
        self._courses: List[Course] = []
        for course in courses:
            self.save(course)

    def get_by_id(self, course_id: str) -> Optional[Course]:
        for course in self._courses:
            if course.course_id == course_id:
                return Course(**vars(course))
        return None

    def list_available_courses(self) -> List[Course]:
        return [
            Course(**vars(course))
            for course in sorted(self._courses, key=lambda c: c.course_id)
            if course.course_type == "free" or course.seats_left > 0
        ]

    def save(self, course: Course) -> None:
        copy = Course(**vars(course))
        for index, stored in enumerate(self._courses):
            if stored.course_id == course.course_id:
                self._courses[index] = copy
                return
        self._courses.append(copy)


# --- the repositories ------------------------------------------------------

def test_a_saved_course_comes_back(sample_course):
    courses = InMemoryCourseRepository()

    courses.save(sample_course)

    assert courses.get_by_id("python-basics") == sample_course


def test_an_unknown_course_id_answers_none():
    assert InMemoryCourseRepository().get_by_id("no-such-course") is None, (
        "get_by_id answers None for an id it does not know. It does not raise, "
        "and it does not return a half-built Course: deciding what a missing "
        "course means is the caller's job."
    )


def test_saving_the_same_id_twice_replaces_it(sample_course):
    courses = InMemoryCourseRepository()
    courses.save(sample_course)
    sample_course.title = "Python Basics, second edition"

    courses.save(sample_course)

    assert len(courses.list_available_courses()) == 1
    assert courses.get_by_id("python-basics").title == "Python Basics, second edition"


def test_what_get_by_id_returns_is_not_what_is_stored(sample_course):
    courses = InMemoryCourseRepository()
    courses.save(sample_course)

    borrowed = courses.get_by_id("python-basics")
    borrowed.enrolled_count = 99

    assert courses.get_by_id("python-basics").enrolled_count == 0, (
        "Changing the object get_by_id handed back changed what is stored. "
        "Hand out copies: a caller that has not called save yet has not saved "
        "anything."
    )


def test_a_full_limited_course_is_not_available(sample_instructor):
    courses = InMemoryCourseRepository(
        [
            Course("free-one", "Free One", "free", capacity=1, enrolled_count=5),
            Course("full-one", "Full One", "limited", capacity=1, enrolled_count=1),
            Course("open-one", "Open One", "limited", capacity=2, enrolled_count=1),
        ]
    )

    available = [course.course_id for course in courses.list_available_courses()]

    assert available == ["free-one", "open-one"], (
        "list_available_courses returned %s. A course with no seat left is not "
        "available; a free course always is." % available
    )


def test_exists_for_finds_the_enrollment_and_nothing_else():
    enrollments = InMemoryEnrollmentRepository()
    enrollments.save(Enrollment("e-1", "python-basics", "s-1"))

    assert enrollments.exists_for("python-basics", "s-1") is True
    assert enrollments.exists_for("python-basics", "s-2") is False
    assert enrollments.exists_for("testing-101", "s-1") is False


# --- the service -----------------------------------------------------------

def test_enrolling_saves_the_enrollment_and_notifies(
    sample_course, sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(sample_course)
    service = build_service(courses, enrollments, fake_notifier)

    enrollment = service.enroll_student("python-basics", sample_student)

    assert isinstance(enrollment, Enrollment), (
        "A successful enrollment answers with an Enrollment, not with a dict. "
        "Compare that with what legacy_booking hands back."
    )
    assert enrollment.course_id == "python-basics"
    assert enrollment.student_id == "s-1"
    assert enrollments.exists_for("python-basics", "s-1") is True
    assert len(fake_notifier.sent) == 1, (
        "The student was enrolled and never told. Notifying is part of the use "
        "case, and the service is what owns it."
    )
    assert fake_notifier.sent[0].recipient == "ada@example.com"


def test_enrolling_takes_a_seat_on_the_course(
    sample_course, sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(sample_course)
    service = build_service(courses, enrollments, fake_notifier)

    service.enroll_student("python-basics", sample_student)

    assert courses.get_by_id("python-basics").enrolled_count == 1, (
        "The enrollment was saved but the course still says nobody is on it. "
        "Count the seat and save the course back."
    )


def test_the_same_student_cannot_take_two_seats(
    sample_course, sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(sample_course)
    service = build_service(courses, enrollments, fake_notifier)
    service.enroll_student("python-basics", sample_student)

    attempt(service, "python-basics", sample_student)

    assert courses.get_by_id("python-basics").enrolled_count == 1
    assert len(fake_notifier.sent) == 1, (
        "The second attempt was refused and the student was told about it "
        "anyway. Nothing should happen after a refusal."
    )


def test_a_full_course_refuses_the_next_student(
    sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    courses.save(Course("testing-101", "Testing 101", "limited", capacity=1))
    service = build_service(courses, enrollments, fake_notifier)
    service.enroll_student("testing-101", sample_student)

    attempt(
        service,
        "testing-101",
        Student("s-2", "Alan Turing", "alan@example.com"),
    )

    assert courses.get_by_id("testing-101").enrolled_count == 1
    assert enrollments.exists_for("testing-101", "s-2") is False


def test_an_unknown_course_enrolls_nobody(
    sample_student, in_memory_repositories, fake_notifier
):
    courses, enrollments = in_memory_repositories
    service = build_service(courses, enrollments, fake_notifier)

    attempt(service, "no-such-course", sample_student)

    assert enrollments.exists_for("no-such-course", "s-1") is False
    assert fake_notifier.sent == []


def test_the_service_does_not_care_which_repository_it_got(
    sample_course, sample_student, fake_notifier
):
    """Same service, same test, a completely different course repository.

    This is the whole return on stage 2. The service depends on the protocol,
    the protocol says nothing about dicts or lists, so swapping the storage is
    a one-line change in the caller and no change at all in the service.
    """
    enrollments = InMemoryEnrollmentRepository()
    courses = ListCourseRepository([sample_course])
    service = build_service(courses, enrollments, fake_notifier)

    enrollment = service.enroll_student("python-basics", sample_student)

    assert enrollment.course_id == "python-basics"
    assert courses.get_by_id("python-basics").enrolled_count == 1
    assert len(fake_notifier.sent) == 1
