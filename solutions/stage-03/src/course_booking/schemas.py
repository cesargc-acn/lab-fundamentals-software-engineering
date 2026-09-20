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

    course_id: str = Field(min_length=1)
    student_id: str = Field(min_length=1)
    name: str = Field(min_length=1)
    email: str
    has_payment_method: bool = False

    @field_validator("email")
    @classmethod
    def email_must_look_like_an_address(cls, value: str) -> str:
        """Reject an address with no @ in it."""
        if "@" not in value:
            raise ValueError("email must contain an @")
        return value


class EnrollmentResponse(BaseModel):
    """What the API hands back once a student holds a seat."""

    enrollment_id: str
    course_id: str
    student_id: str
    status: str
