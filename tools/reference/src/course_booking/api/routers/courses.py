"""HTTP for courses.

A router knows the HTTP vocabulary: paths, status codes, response models.
It knows nothing about enrollment rules, and it never decides what a 404 means.
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
# @text sensible defaults, and slice the list the repository returns. Use
# @text `Query(...)` so the bounds show up in /docs. Nothing tests this one.
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
# @text Finish the two routes below. `POST /courses` creates a course from the
# @text request body and answers 201 with a `CourseResponse`.
# @text `GET /courses/{course_id}` answers with the course, and raises
# @text `CourseNotFoundError` when there is none: the router does not know that
# @text is a 404, and it does not need to. Say `response_model` and
# @text `status_code` in the decorator rather than building a `Response`.
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
