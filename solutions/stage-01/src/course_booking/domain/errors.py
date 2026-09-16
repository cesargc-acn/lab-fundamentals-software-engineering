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

    # TODO [stage-3] 1 (core): Give the error the data its handler will need: store
    #     `course_id` on the exception and hand a readable message to
    #     `super().__init__`.
    pass


class StudentAlreadyEnrolledError(DomainError):
    """Raised when a student already holds a seat on the course."""

    # TODO [stage-3] 1 (core): Same shape as above, with two ids to store this time.
    pass


class EnrollmentNotAllowedError(DomainError):
    """Raised when the enrollment policy says no."""

    # TODO [stage-3] 1 (core): This one also carries `reason`, a sentence a human can
    #     read. The policy answers True or False; the service is what knows why.
    pass
