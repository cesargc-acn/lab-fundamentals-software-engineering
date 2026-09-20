# Stage 4 — notes on this implementation

Read this after your own version is green, or when you are stuck and want to
see one way through. The code next to it is *a* solution, not *the* solution.

**The short version**

- The mapping from domain error to status code lives on the app, once, so no
  router ever has to know that a missing course is a 404.
- `dependencies.py` is the only file that knows the concrete classes exist.
- Routes ask with `Depends` instead of building, which is the single reason
  tests can substitute the repositories.
- Reads go straight to the repository and writes go through the service,
  because only one of the two has rules attached to it.

## Why this implementation

The exception handlers live in `main.py` and not in the routers. A router that catches `CourseNotFoundError` and returns a 404 is not wrong, it just has to be written again in the next router, and the third time somebody will pick 400 instead of 404 and nobody will notice for a month. Registering the handler on the app makes the mapping from domain error to status code a property of the application, decided once, and it is the reason `POST /enrollments` can answer 404, 409 and 422 without containing a single `try`.

The providers in `dependencies.py` are the composition root: the one file that knows `InMemoryCourseRepository` exists. `lru_cache(maxsize=1)` is what makes the repositories singletons — the first request builds one, every later request gets the same object, which is what "the application has one database" means when the database is a dict. It is also why the tests can replace them through `app.dependency_overrides` without touching a line of application code.

`get_enrollment_service` asks for its collaborators with `Depends` rather than calling the other providers itself. That is not ceremony: it is what lets a test override the course repository and have the service that gets built one layer up use the override, without the service knowing that anything unusual happened.

The reads go through the course repository and the enrollment goes through the service. That asymmetry is deliberate. Reading a course is a lookup with no rule attached to it, and wrapping it in a service method would add a layer that only forwards. The enrollment has four rules and a notification, and none of that belongs in a route handler.

## Other valid approaches

If you wrapped the service call in `try/except` inside the router and returned `JSONResponse` yourself, the HTTP tests pass. It stops scaling at the second router, which is exactly when it stops being obvious.

If you registered a single handler for `DomainError` and mapped the concrete class to a status code inside it, that is a good design, and a better one than this if you expect a dozen error types.

If you put `Depends(get_course_repository)` on the `APIRouter` instead of on each route, that also works and is tidier once every route in a file needs the same dependency.

## Theory reference

Blocks 7 and 9: routing, `Depends`, and status codes that carry information.

## If you have spare time

Add `DELETE /enrollments/{enrollment_id}`. It needs a repository method you have not written, an error for an enrollment that does not exist, a decision about whether the seat comes back, and a status code — 204 with no body, or 200 with the cancelled enrollment. Write the tests first and let them make the choices. There is no reference solution for it.
