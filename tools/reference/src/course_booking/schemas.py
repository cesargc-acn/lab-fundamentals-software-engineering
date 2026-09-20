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

    # @todo stage=3 id=3 kind=core
    # @text Declare the fields a client may send:
    # @text - `course_id`, `student_id` and `name`: strings, none of them empty;
    # @text - `email`: a string;
    # @text - `has_payment_method`: a bool that defaults to False, because a
    # @text client that says nothing has not said yes.
    # @text | `CreateCourseRequest` above shows how to say "this string may not
    # @text be empty" with `Field(min_length=1)`.
    # @stub pass
    # @at 3
    course_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: str
    has_payment_method: bool = False
    # @end

    # @todo stage=3 id=4 kind=optional
    # @text Add a field validator on `email`, the way
    # @text `course_type_must_be_known` does it above. Pydantic has already
    # @text checked the value is a string; your check runs after that. Reject
    # @text it by raising `ValueError` with a message a human can read, and
    # @text return the value when it is fine.
    # @stub none
    # @at 3
    @field_validator("email")
    @classmethod
    def email_must_look_like_an_address(cls, value: str) -> str:
        """Reject an address with no @ in it."""
        if "@" not in value:
            raise ValueError("email must contain an @")
        return value
    # @end


class EnrollmentResponse(BaseModel):
    """What the API hands back once a student holds a seat."""

    # @todo stage=3 id=3 kind=core
    # @text Four string fields, and no validation to add: `enrollment_id`,
    # @text `course_id`, `student_id`, `status`.
    # @text | Notice what is not here. The email came in on the request and
    # @text does not go out on the response, and being able to make that
    # @text decision is the entire reason a response model is a separate class.
    # @stub pass
    # @at 3
    enrollment_id: str
    course_id: str
    student_id: str
    status: str
    # @end
