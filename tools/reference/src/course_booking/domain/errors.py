"""What the domain refuses to do, and why.

Every error carries the data a caller needs to explain itself. Nothing in here
knows about HTTP: turning an error into a status code is the API's job, and it
happens in one place, `main.py`.

Stage 3, first half. Each class needs one `__init__` that does two things:
store the ids as attributes, so a caller never has to parse a message, and pass
a readable sentence to `super().__init__`, because that sentence is what the
client will read as `detail` once stage 4 wires the handlers up.

    class OrderTooLargeError(DomainError):
        def __init__(self, order_id: str, limit: int) -> None:
            self.order_id = order_id
            self.limit = limit
            super().__init__("Order %r is over the limit of %d" % (order_id, limit))
"""

from __future__ import annotations


class DomainError(Exception):
    """Given. The root of the family, so one `except` can catch all of them."""


class CourseNotFoundError(DomainError):
    """Raised when a course id matches no course."""

    # @todo stage=3 id=1 kind=core
    # @text Write `__init__(self, course_id: str)`. Store `course_id` as an
    # @text attribute, then hand a readable message to `super().__init__`. The
    # @text test reads `error.course_id`, so the attribute is not optional.
    # @stub pass
    # @at 3
    def __init__(self, course_id: str) -> None:
        self.course_id = course_id
        super().__init__("Course %r does not exist" % course_id)
    # @end


class StudentAlreadyEnrolledError(DomainError):
    """Raised when a student already holds a seat on the course."""

    # @todo stage=3 id=1 kind=core
    # @text Same shape as above: `__init__(self, course_id, student_id)`, with
    # @text two ids to store this time, and a message that mentions both.
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
    # @text `__init__(self, course_id, student_id, reason)`. The third one is a
    # @text sentence a human can read, and it matters: the policy only answers
    # @text True or False, so the service is the only place that knows why the
    # @text answer was no. Store all three and mention the reason in the
    # @text message.
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
