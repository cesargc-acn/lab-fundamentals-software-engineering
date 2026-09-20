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

    # TODO [stage-3] 1 (core): Write `__init__(self, course_id: str)`. Store
    #     `course_id` as an attribute, then hand a readable message to
    #     `super().__init__`. The test reads `error.course_id`, so the attribute is
    #     not optional.
    pass


class StudentAlreadyEnrolledError(DomainError):
    """Raised when a student already holds a seat on the course."""

    # TODO [stage-3] 1 (core): Same shape as above: `__init__(self, course_id,
    #     student_id)`, with two ids to store this time, and a message that mentions
    #     both.
    pass


class EnrollmentNotAllowedError(DomainError):
    """Raised when the enrollment policy says no."""

    # TODO [stage-3] 1 (core): `__init__(self, course_id, student_id, reason)`. The
    #     third one is a sentence a human can read, and it matters: the policy only
    #     answers True or False, so the service is the only place that knows why the
    #     answer was no. Store all three and mention the reason in the message.
    pass
