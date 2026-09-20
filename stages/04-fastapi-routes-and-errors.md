# Stage 4 · FastAPI: routes, Depends and HTTP codes

**Files you will touch:** `src/course_booking/api/routers/courses.py`,
`src/course_booking/api/routers/enrollments.py`,
`src/course_booking/api/dependencies.py`, `src/course_booking/main.py`.
**Run the tests with:** `python workshop.py test 4`

---

## New ideas in this stage

**`Depends`.** FastAPI's dependency injection. You declare a parameter whose
default is `Depends(some_function)`; FastAPI calls that function before your
route runs and passes the result in.

```python
def get_clock() -> Clock:            # a "provider": builds the thing
    return SystemClock()

@router.get("/now")
def now(clock: Clock = Depends(get_clock)) -> str:   # the route never builds it
    return clock.now().isoformat()
```

Because the route asks rather than builds, a test can say
`app.dependency_overrides[get_clock] = lambda: FrozenClock()` and change what
the route gets without touching the route. That is exactly what the `client`
fixture in `tests/conftest.py` does with the repositories.

**Exception handler.** A function registered on the app with
`@app.exception_handler(SomeError)`. When *any* route raises `SomeError`,
FastAPI calls it and sends back whatever it returns. It is what lets a router
raise a domain error without ever mentioning a status code.

**The status codes this stage uses**

| Code | Means | Here |
|---|---|---|
| 201 | Created | a `POST` that created something. Not the default — you must say so |
| 404 | Not Found | `CourseNotFoundError` |
| 409 | Conflict | `StudentAlreadyEnrolledError`: the request fights the state the server is already in |
| 422 | Unprocessable | well-formed request, refused anyway: a bad field, or `EnrollmentNotAllowedError` |

Anything else the statement uses is in [GLOSSARY.md](../GLOSSARY.md).

## The problem

Everything you have built so far is reachable only from a test. It needs a way
in. The risk of adding one is that the routes quietly become the application:
first a small `if`, then a lookup, then a rule, and the service turns into a
place where data structures are passed through on the way to the real logic.

## What you will build

- Routes that speak HTTP and nothing else.
- One composition root, where the concrete classes are chosen.
- Three handlers that map a domain error to a status code, once, for every
  route that will ever exist.

## Your tasks

Do them in this order — the routes will not run until the providers exist.

**1. core — the course routes, in `api/routers/courses.py`**

`GET /courses` is given and working, at the top of the file. Read it before you
write anything: it shows the decorator, the `Depends` parameter and the
`CourseResponse.from_course` mapping you need for both of the others.

- `POST /courses` → **201** with a `CourseResponse`. Build a `Course` from the
  request body, `save` it, return the response model. Say `response_model=...`
  and `status_code=201` in the decorator rather than building a `Response` by
  hand.
- `GET /courses/{course_id}` → **200** with a `CourseResponse`. When
  `get_by_id` answers `None`, `raise CourseNotFoundError(course_id)`. The
  router does not know that is a 404, and it does not need to.

**2. core — `POST /enrollments`, in `api/routers/enrollments.py`**

Three steps: turn `CreateEnrollmentRequest` into a `Student`, hand it and the
`course_id` to `service.enroll_student(...)`, return an `EnrollmentResponse`
built from what comes back. Answer **201**.

Catch nothing. All three domain errors travel straight out of the route and
`main.py` turns each of them into a status code, once, for every router.

**3. core — the providers, in `api/dependencies.py`**

- `get_course_repository()` → an `InMemoryCourseRepository`. One line.
- `get_enrollment_repository()` → the enrollment one. Same again.
- `get_notification_sender()` → an `EmailNotificationSender`. (If you did the
  optional `create_notification_sender` in stage 2, call it instead — this is
  exactly the caller it was written for.)
- `get_enrollment_service(...)` → build and return the `EnrollmentService`.
  Three of its four collaborators already arrived as arguments, because
  `Depends` resolved them before this function ran. The fourth, the policy,
  comes from `default_enrollment_policy()`.

The `@lru_cache(maxsize=1)` decorators are already there, and they are what
make the repositories shared: the first request builds one, every later request
gets the same object. That is what "the application has one database" means
when the database is a dict.

**4. core — the three exception handlers, in `main.py`**

```python
@app.exception_handler(CourseNotFoundError)
def handle_course_not_found(request: Request, exc: CourseNotFoundError) -> JSONResponse:
    return JSONResponse(status_code=404, content={"detail": str(exc)})
```

That is the first one, complete — it is the shape, not a shortcut. Write the
other two: `StudentAlreadyEnrolledError` → 409, `EnrollmentNotAllowedError` →
422. Every body carries a `detail` the client can show, and `str(exc)` is the
message you wrote into the exception in stage 3.

This is the only file in the project where a domain error and an HTTP status
code are allowed to meet.

**5. optional — `limit` and `offset` on `GET /courses`**

Add them as query parameters with sensible defaults and slice the list the
repository returns. Use `Query(...)` so the bounds show up in `/docs`. No test
covers the pagination.

### Already written for you

`GET /courses`, `GET /health`, and `POST /enrollments/payment` — the last one
is the only `async def` route in the project, and stage 5 is about the code it
calls, not about the route.

## Check your work

```
python workshop.py test 4
python workshop.py run        # then open http://127.0.0.1:8000/docs
```

`/docs` is worth two minutes: it is generated from your `response_model` and
`status_code` declarations, so anything missing there is missing from the
decorator.

`test_the_use_case_works_without_an_http_request` is the last test in the file
and the one that matters most. It runs the same enrollment with no client, no
router and no FastAPI at all. If it fails while the HTTP tests pass, something
the domain needs has moved into a route handler.

**Done when:**

- [ ] `python workshop.py test 4` is green
- [ ] stages 0 to 3 are still green
- [ ] no `try` in `api/routers/`, and no 404, 409 or 422 in them either —
      `status_code=201` in a decorator is the router describing its own
      success, which is its job
- [ ] `grep -rn "TODO \[stage-4\]" src/` shows only the optional task, if you
      skipped it

## Common mistakes

- **Getting 200 instead of 201.** `status_code=201` goes in the decorator, not
  in the body.
- **Catching the domain errors in the router.** The HTTP tests pass, and you
  have just written code you will have to write again in the next router.
- **Calling a provider instead of declaring it.** `courses =
  get_course_repository()` inside the route works right up until a test tries
  to override it, and then it silently ignores the override.
- **Returning the entity from a route.** Routes return schemas.
  `CourseResponse.from_course(course)` is the only place that mapping lives.
- **Writing the handlers above `include_router`.** Order does not matter for
  handlers, but a handler defined inside a router file does not apply to the
  others — they belong on the app.

Stuck? `python workshop.py hint 4`.
