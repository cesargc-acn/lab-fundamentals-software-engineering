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


# TODO [stage-4] 5 (optional): Add `limit` and `offset` query parameters to the route
#     below, with sensible defaults, and slice the list the repository returns. Use
#     `Query(...)` so the bounds show up in /docs. Nothing tests this one.
@router.get("", response_model=List[CourseResponse])
def list_courses(
    courses: CourseRepository = Depends(get_course_repository),
) -> List[CourseResponse]:
    """Given. Every course a student could still join."""
    return [CourseResponse.from_course(course) for course in courses.list_available_courses()]


# TODO [stage-4] 1 (core): Finish the two routes below. `POST /courses` creates a
#     course from the request body and answers 201 with a `CourseResponse`. `GET
#     /courses/{course_id}` answers with the course, and raises `CourseNotFoundError`
#     when there is none: the router does not know that is a 404, and it does not need
#     to. Say `response_model` and `status_code` in the decorator rather than building
#     a `Response`.
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
