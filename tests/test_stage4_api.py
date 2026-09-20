"""Stage 4. The HTTP contract, and a check that it is only a contract.

Every test but the last one talks to the API over HTTP. The last one runs the
same use case straight against the service. If that one fails while the HTTP
ones pass, logic has leaked into a router.
"""

from __future__ import annotations

import pytest

from course_booking.domain.models import Student
from course_booking.domain.policies import default_enrollment_policy
from course_booking.services.enrollment_service import EnrollmentService

pytestmark = pytest.mark.stage4

FREE_COURSE = {
    "course_id": "python-basics",
    "title": "Python Basics",
    "course_type": "free",
    "capacity": 2,
    "price": 0.0,
}
ONE_SEAT_COURSE = {
    "course_id": "testing-101",
    "title": "Testing 101",
    "course_type": "limited",
    "capacity": 1,
    "price": 0.0,
}


def enrollment_payload(student_id: str = "s-1", course_id: str = "python-basics"):
    return {
        "course_id": course_id,
        "student_id": student_id,
        "name": "Ada Lovelace",
        "email": "%s@example.com" % student_id,
        "has_payment_method": False,
    }


# --- courses ---------------------------------------------------------------

def test_creating_a_course_answers_201_and_the_course(client):
    response = client.post("/courses", json=FREE_COURSE)

    assert response.status_code == 201, (
        "Creating a resource answers 201, not 200. Say it in the decorator: "
        "status_code=201. Got %d: %s" % (response.status_code, response.text)
    )
    body = response.json()
    assert body["course_id"] == "python-basics"
    assert body["seats_left"] == 2, (
        "CourseResponse carries seats_left, which the entity computes. A "
        "response model is allowed to be more useful than the row behind it."
    )


def test_reading_a_course_back(client):
    client.post("/courses", json=FREE_COURSE)

    response = client.get("/courses/python-basics")

    assert response.status_code == 200
    assert response.json()["title"] == "Python Basics"


def test_reading_a_course_that_does_not_exist_answers_404(client):
    response = client.get("/courses/no-such-course")

    assert response.status_code == 404, (
        "A missing course is a 404. The router raised CourseNotFoundError and "
        "never mentioned a status code: the handler in main.py is what turns "
        "it into one. Got %d." % response.status_code
    )
    assert "detail" in response.json()


def test_listing_courses_leaves_out_the_full_ones(client):
    client.post("/courses", json=FREE_COURSE)
    client.post("/courses", json=ONE_SEAT_COURSE)
    client.post("/enrollments", json=enrollment_payload(course_id="testing-101"))

    body = client.get("/courses").json()

    assert [course["course_id"] for course in body] == ["python-basics"]


def test_an_unknown_course_type_is_rejected_before_the_domain_sees_it(client):
    response = client.post("/courses", json=dict(FREE_COURSE, course_type="cooking"))

    assert response.status_code == 422, (
        "The schema rejects a course type nothing can enroll on, and it does "
        "it before any of your code runs. Got %d." % response.status_code
    )


# --- enrollments -----------------------------------------------------------

def test_enrolling_answers_201_and_the_enrollment(client):
    client.post("/courses", json=FREE_COURSE)

    response = client.post("/enrollments", json=enrollment_payload())

    assert response.status_code == 201, (
        "Got %d: %s" % (response.status_code, response.text)
    )
    body = response.json()
    assert body["course_id"] == "python-basics"
    assert body["student_id"] == "s-1"
    assert body["status"] == "confirmed"
    assert body["enrollment_id"], "The response carries the id of what was created."


def test_enrolling_twice_answers_409(client):
    client.post("/courses", json=FREE_COURSE)
    client.post("/enrollments", json=enrollment_payload())

    response = client.post("/enrollments", json=enrollment_payload())

    assert response.status_code == 409, (
        "The second request conflicts with the state the server is already in, "
        "and 409 is the word for that. Got %d." % response.status_code
    )


def test_enrolling_on_a_full_course_answers_422(client):
    client.post("/courses", json=ONE_SEAT_COURSE)
    client.post("/enrollments", json=enrollment_payload("s-1", "testing-101"))

    response = client.post("/enrollments", json=enrollment_payload("s-2", "testing-101"))

    assert response.status_code == 422, (
        "The request was well formed and the domain still said no: that is a "
        "422, not a 400 and not a 409. Got %d." % response.status_code
    )


def test_enrolling_on_an_unknown_course_answers_404(client):
    response = client.post("/enrollments", json=enrollment_payload(course_id="nope"))

    assert response.status_code == 404


def test_an_enrollment_request_without_a_student_id_answers_422(client):
    payload = enrollment_payload()
    del payload["student_id"]

    assert client.post("/enrollments", json=payload).status_code == 422


def test_the_health_route_is_up(client):
    assert client.get("/health").json() == {"status": "ok"}


# --- the same use case, without HTTP ---------------------------------------

def test_the_use_case_works_without_an_http_request(
    sample_course, sample_student, in_memory_repositories, fake_notifier
):
    """No client, no router, no FastAPI. Same result.

    If this test fails and the HTTP ones pass, something the domain needs is
    living in a route handler: move it into the service and call it from both.
    """
    courses, enrollments = in_memory_repositories
    courses.save(sample_course)
    service = EnrollmentService(
        courses=courses,
        enrollments=enrollments,
        policy=default_enrollment_policy(),
        notifier=fake_notifier,
    )

    enrollment = service.enroll_student("python-basics", sample_student)

    assert enrollment.status == "confirmed"
    assert courses.get_by_id("python-basics").enrolled_count == 1
    assert len(fake_notifier.sent) == 1
