"""What crosses the wire.

A schema is not an entity. `Course` is what the domain reasons about;
`CourseResponse` is what a client is allowed to see. Keeping them apart is why
you can rename a field in the domain without breaking every consumer.

Stage 3, second half. `CreateCourseRequest` and `CourseResponse` are given and
complete: read them first, because the two classes you have to write are the
same idea with different fields.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field, field_validator

from .domain.models import COURSE_TYPES, Course


class CreateCourseRequest(BaseModel):
    """Given. What a client may send to create a course."""

    course_id: str = Field(min_length=1)
    title: str = Field(min_length=1)
    course_type: str
    capacity: int = Field(ge=0)
    price: float = Field(default=0.0, ge=0.0)

    @field_validator("course_type")
    @classmethod
    def course_type_must_be_known(cls, value: str) -> str:
        """Reject a course type nothing knows how to enroll on."""
        if value not in COURSE_TYPES:
            raise ValueError("course_type must be one of: %s" % ", ".join(COURSE_TYPES))
        return value


class CourseResponse(BaseModel):
    """Given. What a client gets back when it asks about a course."""

    course_id: str
    title: str
    course_type: str
    capacity: int
    price: float
    enrolled_count: int
    seats_left: int
    instructor_name: Optional[str] = None

    @classmethod
    def from_course(cls, course: Course) -> "CourseResponse":
        """Map the entity onto the response. The only place that mapping lives."""
        return cls(
            course_id=course.course_id,
            title=course.title,
            course_type=course.course_type,
            capacity=course.capacity,
            price=course.price,
            enrolled_count=course.enrolled_count,
            seats_left=course.seats_left,
            instructor_name=course.instructor.name if course.instructor else None,
        )


class CreateEnrollmentRequest(BaseModel):
    """What a client sends to put a student on a course."""

    # TODO [stage-3] 3 (core): Declare the fields a client may send:
    #     - `course_id`, `student_id` and `name`: strings, none of them empty;
    #     - `email`: a string;
    #     - `has_payment_method`: a bool that defaults to False, because a client that
    #       says nothing has not said yes.
    #     `CreateCourseRequest` above shows how to say "this string may not be empty"
    #     with `Field(min_length=1)`.
    pass

    # TODO [stage-3] 4 (optional): Add a field validator on `email`, the way
    #     `course_type_must_be_known` does it above. Pydantic has already checked the
    #     value is a string; your check runs after that. Reject it by raising
    #     `ValueError` with a message a human can read, and return the value when it
    #     is fine.


class EnrollmentResponse(BaseModel):
    """What the API hands back once a student holds a seat."""

    # TODO [stage-3] 3 (core): Four string fields, and no validation to add:
    #     `enrollment_id`, `course_id`, `student_id`, `status`.
    #     Notice what is not here. The email came in on the request and does not go
    #     out on the response, and being able to make that decision is the entire
    #     reason a response model is a separate class.
    pass
