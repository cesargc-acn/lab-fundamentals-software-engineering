"""The application object, and nothing else.

Create the app, plug the routers in, say what each domain error means in HTTP.
If you ever find yourself writing an `if` in this file, it belongs somewhere
else.

Stage 4. The app, the routers and `/health` are given; the exception handlers
at the bottom are yours. A handler registered here applies to every route in
every router, which is why no router in this project contains a single `try`.
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
# @text Register one handler per domain error with `@app.exception_handler(...)`.
# @text Each takes `(request: Request, exc: TheError)` and returns a
# @text `JSONResponse` whose body carries a `detail` the client can show --
# @text `str(exc)` is the message you wrote into the exception in stage 3.
# @text - `CourseNotFoundError` -> 404, nothing to enroll on;
# @text - `StudentAlreadyEnrolledError` -> 409, the request fights the state
# @text the server is already in;
# @text - `EnrollmentNotAllowedError` -> 422, well formed and refused anyway.
# @text | This is the only file in the project where a domain error and an HTTP
# @text status code are allowed to meet. The full statement in
# @text stages/04-fastapi-routes-and-errors.md shows the first handler in full.
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
