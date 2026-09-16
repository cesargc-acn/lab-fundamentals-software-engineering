# Stage 4 · FastAPI: routes, Depends and HTTP codes

*About 30 minutes.*

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

In `api/routers/courses.py`, `api/routers/enrollments.py`,
`api/dependencies.py` and `main.py`.

1. **core** — `POST /courses` (201) and `GET /courses/{course_id}`. When the
   course is missing, raise `CourseNotFoundError`. The router does not know
   that is a 404.
2. **core** — `POST /enrollments`, answering 201. Turn the request into a
   `Student`, hand it to the service, return an `EnrollmentResponse`.
3. **core** — the providers in `dependencies.py`, consumed with `Depends`.
4. **core** — the three exception handlers in `main.py`:
   `CourseNotFoundError` → 404, `StudentAlreadyEnrolledError` → 409,
   `EnrollmentNotAllowedError` → 422.
5. **optional** — `limit` and `offset` on `GET /courses`. That route is given,
   working, at the top of `courses.py`. No test covers the pagination.

`GET /courses` and `GET /health` are given. Read the first one before you write
the other two.

## Check your work

```
python workshop.py test 4
python workshop.py run        # then open http://127.0.0.1:8000/docs
```

The last test in the file runs the same enrollment with no client, no router
and no FastAPI at all. If it fails while the HTTP tests pass, something the
domain needs has moved into a route handler.

## Theory reference

Blocks 7 and 9: routing, dependency injection with `Depends`, and choosing a
status code that means something.
