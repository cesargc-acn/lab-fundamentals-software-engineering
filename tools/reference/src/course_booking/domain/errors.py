"""What the domain refuses to do, and why.

Every error carries the data a caller needs to explain itself. Nothing in here
knows about HTTP: turning an error into a status code is the API's job, and it
happens in one place, `main.py`.
"""

from __future__ import annotations


class DomainError(Exception):
    """Given. The root of the family, so one `except` can catch all of them."""


class CourseNotFoundError(DomainError):
    """Raised when a course id matches no course."""

    # @todo stage=3 id=1 kind=core
    # @text Give the error the data its handler will need: store `course_id` on
    # @text the exception and hand a readable message to `super().__init__`.
    # @stub pass
    # @at 3
    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        super().__init__("Course %r does not exist" % course_id)
    # @end


class StudentAlreadyEnrolledError(DomainError):
    """Raised when a student already holds a seat on the course."""

    # @todo stage=3 id=1 kind=core
    # @text Same shape as above, with two ids to store this time.
    # @stub pass
    # @at 3
    def __init__(self, course_id: str, student_id: str) -> None:
        self.course_id = course_id
        self.student_id = student_id
        super().__init__(
            "Student %r is already enrolled on course %r" % (student_id, course_id)
        )
    # @end


class EnrollmentNotAllowedError(DomainError):
    """Raised when the enrollment policy says no."""

    # @todo stage=3 id=1 kind=core
    # @text This one also carries `reason`, a sentence a human can read. The
    # @text policy answers True or False; the service is what knows why.
    # @stub pass
    # @at 3
    def __init__(self, course_id: str, student_id: str, reason: str) -> None:
        self.course_id = course_id
        self.student_id = student_id
        self.reason = reason
        super().__init__(
            "Student %r cannot enroll on course %r: %s" % (student_id, course_id, reason)
        )
    # @end
