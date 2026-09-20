"""HTTP for courses.

A router knows the HTTP vocabulary: paths, status codes, response models.
It knows nothing about enrollment rules, and it never decides what a 404 means.

Stage 4. `GET /courses` below is given and working: read it first, because it
already shows the three things the two routes you have to write need -- the
decorator, the `Depends` parameter, and `CourseResponse.from_course`.
"""

from __future__ import annotations

from typing import List

from fastapi import APIRouter, Depends, Query

from ...domain.errors import CourseNotFoundError
from ...domain.models import Course
from ...repositories import CourseRepository
from ...schemas import CourseResponse, CreateCourseRequest
from ..dependencies import get_course_repository

router = APIRouter(prefix="/courses", tags=["courses"])


# TODO [stage-4] 5 (optional): Add `limit` and `offset` query parameters to the route
#     below, with sensible defaults, and slice the list the repository returns.
#     Declare them with `Query(default=..., ge=..., le=...)` so the bounds show up in
#     /docs and FastAPI rejects a negative offset for you. Nothing tests this one.
@router.get("", response_model=List[CourseResponse])
def list_courses(
    courses: CourseRepository = Depends(get_course_repository),
) -> List[CourseResponse]:
    """Given. Every course a student could still join."""
    return [CourseResponse.from_course(course) for course in courses.list_available_courses()]


# TODO [stage-4] 1 (core): Finish the two routes below.
#     - `POST /courses`: build a `Course` from the request body, `save` it, and answer
#       201 with a `CourseResponse`. 201 is not the default, so say `status_code=201`
#       in the decorator rather than building a `Response`.
#     - `GET /courses/{course_id}`: return the course. When `get_by_id` answers None,
#       `raise CourseNotFoundError(course_id)` and stop there. The router does not
#       know that is a 404 and does not need to; the handler in main.py decides.
#     Say `response_model=CourseResponse` in both decorators, the way the given route
#     above does, so /docs describes what comes back.
@router.post("")
def create_course(
    payload: CreateCourseRequest,
    courses: CourseRepository = Depends(get_course_repository),
) -> CourseResponse:
    """Create a course and return it."""
    raise NotImplementedError("TODO [stage-4] 1")


@router.get("/{course_id}")
def get_course(
    course_id: str,
    courses: CourseRepository = Depends(get_course_repository),
) -> CourseResponse:
    """Return one course by id."""
    raise NotImplementedError("TODO [stage-4] 1")
