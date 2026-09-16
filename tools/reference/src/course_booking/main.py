"""The application object, and nothing else.

Create the app, plug the routers in, say what each domain error means in HTTP.
If you ever find yourself writing an `if` in this file, it belongs somewhere
else.
"""

from __future__ import annotations

from typing import Dict

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse

from .api.routers import courses, enrollments
from .domain.errors import (
    CourseNotFoundError,
    EnrollmentNotAllowedError,
    StudentAlreadyEnrolledError,
)

app = FastAPI(
    title="Course Booking API",
    version="0.1.0",
    description="The API you build during the Fundamentals of Software Engineering lab.",
)

app.include_router(courses.router)
app.include_router(enrollments.router)


@app.get("/health", tags=["meta"])
def health() -> Dict[str, str]:
    """Given. Something to curl while the server starts."""
    return {"status": "ok"}


# @todo stage=4 id=4 kind=core
# @text Register one exception handler per domain error, with
# @text `@app.exception_handler(...)`. `CourseNotFoundError` is a 404,
# @text `StudentAlreadyEnrolledError` a 409, `EnrollmentNotAllowedError` a 422.
# @text Each one returns a `JSONResponse` whose body carries a `detail` the
# @text client can show. This is the only file in the project where a domain
# @text error and an HTTP status code are allowed to meet.
# @stub none
# @at 4
@app.exception_handler(CourseNotFoundError)
def handle_course_not_found(request: Request, exc: CourseNotFoundError) -> JSONResponse:
    """The course does not exist: nothing to enroll on."""
    return JSONResponse(status_code=404, content={"detail": str(exc)})


@app.exception_handler(StudentAlreadyEnrolledError)
def handle_already_enrolled(
    request: Request, exc: StudentAlreadyEnrolledError
) -> JSONResponse:
    """The request conflicts with the state the server is already in."""
    return JSONResponse(status_code=409, content={"detail": str(exc)})


@app.exception_handler(EnrollmentNotAllowedError)
def handle_not_allowed(
    request: Request, exc: EnrollmentNotAllowedError
) -> JSONResponse:
    """Well-formed request, and the domain still says no."""
    return JSONResponse(status_code=422, content={"detail": str(exc)})
# @end
