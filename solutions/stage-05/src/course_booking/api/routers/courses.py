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


@router.get("", response_model=List[CourseResponse])
def list_courses(
    limit: int = Query(default=20, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    courses: CourseRepository = Depends(get_course_repository),
) -> List[CourseResponse]:
    """Given. Every course a student could still join, one page at a time."""
    available = courses.list_available_courses()[offset:offset + limit]
    return [CourseResponse.from_course(course) for course in available]


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
