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


# TODO [stage-4] 4 (core): Register one exception handler per domain error, with
#     `@app.exception_handler(...)`. `CourseNotFoundError` is a 404,
#     `StudentAlreadyEnrolledError` a 409, `EnrollmentNotAllowedError` a 422. Each one
#     returns a `JSONResponse` whose body carries a `detail` the client can show. This
#     is the only file in the project where a domain error and an HTTP status code are
#     allowed to meet.
