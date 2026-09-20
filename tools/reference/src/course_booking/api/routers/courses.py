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


# @todo stage=4 id=5 kind=optional
# @text Add `limit` and `offset` query parameters to the route below, with
# @text sensible defaults, and slice the list the repository returns. Declare
# @text them with `Query(default=..., ge=..., le=...)` so the bounds show up in
# @text /docs and FastAPI rejects a negative offset for you. Nothing tests this
# @text one.
# @at 0
@router.get("", response_model=List[CourseResponse])
def list_courses(
    courses: CourseRepository = Depends(get_course_repository),
) -> List[CourseResponse]:
    """Given. Every course a student could still join."""
    return [CourseResponse.from_course(course) for course in courses.list_available_courses()]
# @at 4
@router.get("", response_model=List[CourseResponse])
def list_courses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    courses: CourseRepository = Depends(get_course_repository),
) -> List[CourseResponse]:
    """Given. Every course a student could still join, one page at a time."""
    available = courses.list_available_courses()[offset:offset + limit]
    return [CourseResponse.from_course(course) for course in available]
# @end


# @todo stage=4 id=1 kind=core
# @text Finish the two routes below.
# @text - `POST /courses`: build a `Course` from the request body, `save` it,
# @text and answer 201 with a `CourseResponse`. 201 is not the default, so say
# @text `status_code=201` in the decorator rather than building a `Response`.
# @text - `GET /courses/{course_id}`: return the course. When `get_by_id`
# @text answers None, `raise CourseNotFoundError(course_id)` and stop there.
# @text The router does not know that is a 404 and does not need to; the
# @text handler in main.py decides.
# @text | Say `response_model=CourseResponse` in both decorators, the way the
# @text given route above does, so /docs describes what comes back.
# @at 0
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
# @at 4
@router.post("", response_model=CourseResponse, status_code=201)
def create_course(
    payload: CreateCourseRequest,
    courses: CourseRepository = Depends(get_course_repository),
) -> CourseResponse:
    """Create a course and return it."""
    course = Course(
        course_id=payload.course_id,
        title=payload.title,
        course_type=payload.course_type,
        capacity=payload.capacity,
        price=payload.price,
    )
    courses.save(course)
    return CourseResponse.from_course(course)


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: str,
    courses: CourseRepository = Depends(get_course_repository),
) -> CourseResponse:
    """Return one course by id."""
    course = courses.get_by_id(course_id)
    if course is None:
        raise CourseNotFoundError(course_id)
    return CourseResponse.from_course(course)
# @end
