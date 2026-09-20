# Stage 3 · Domain errors and validation

**Files you will touch:** `src/course_booking/domain/errors.py`,
`src/course_booking/services/enrollment_service.py`,
`src/course_booking/schemas.py`.
**Run the tests with:** `python workshop.py test 3`

---

## New ideas in this stage

**Domain error.** An exception that names something the business refuses to do
— `CourseNotFoundError`, not `KeyError`. It carries the data a caller needs as
*attributes*, so nobody has to parse an error message to find out which course
was missing.

```python
class DomainError(Exception):
    """The root of the family."""

class CourseNotFoundError(DomainError):
    def __init__(self, course_id: str) -> None:
        self.course_id = course_id                       # data, for the caller
        super().__init__("Course %r does not exist" % course_id)   # words, for a human
```

A caller who does not care which failure happened writes
`except DomainError:`; one who does writes `except CourseNotFoundError as error:`
and reads `error.course_id`.

**Schema.** A Pydantic class describing data that crosses the boundary of your
application: what a client may send in, what you agree to send back. It is not
the entity. `Course` is what the domain reasons about; `CourseResponse` is what
a client is allowed to see.

**Structured logging.** Writing a log line as named fields
(`operation="enroll_student"`, `error_type="CourseNotFoundError"`) instead of
as one sentence, so that six months later somebody can filter by `error_type`.

All three, and anything else the statement uses, are in
[GLOSSARY.md](../GLOSSARY.md).

## The problem

Your service answers `None` when the course does not exist and `False` when the
enrollment is refused, and there are two different reasons it might be refused.
A caller gets a falsy value and has to guess which of the four things happened.
Nobody checks. Nobody logs. The support ticket says "it didn't work".

## What you will build

- Three named errors under one base class, each carrying the data a caller
  needs.
- A service whose return type is the truth: if it comes back, the student is
  in.
- Request and response models, so what may cross the wire is written down.

## Your tasks

**1. core — the three errors, in `domain/errors.py`**

Write the constructor of each. `DomainError` is given: it is the root that lets
one `except` catch the family, and it needs no code of its own.

| Error | Stores | Test reads |
|---|---|---|
| `CourseNotFoundError` | `course_id` | `.course_id` |
| `StudentAlreadyEnrolledError` | `course_id`, `student_id` | both |
| `EnrollmentNotAllowedError` | `course_id`, `student_id`, `reason` | `.reason` |

Each one also passes a readable message to `super().__init__(...)` — that
message is what ends up in the HTTP response body in stage 4, so write it for
somebody who will read it in a support ticket. `reason` is a sentence a human
can read: the policy answers True or False, and the service is what knows why.

**2. core — raise instead of return, in `services/enrollment_service.py`**

Replace the three refusal signals from stage 2 with the errors you just wrote,
and call `_log_failure` immediately before each `raise`:

| Was | Becomes |
|---|---|
| `return None` (no such course) | `_log_failure("CourseNotFoundError", ...)` then `raise CourseNotFoundError(...)` |
| `return False` (already enrolled) | `_log_failure("StudentAlreadyEnrolledError", ...)` then `raise StudentAlreadyEnrolledError(...)` |
| `return False` (policy said no) | `_log_failure("EnrollmentNotAllowedError", ...)` then `raise EnrollmentNotAllowedError(...)` |

`_log_failure(error_type, course_id, student_id)` is given, and the fields it
writes are the ones the theory asks for. `_rejection_reason(course)` is given
too: it turns a policy's "no" into the sentence `EnrollmentNotAllowedError`
needs.

Then change the signature. It goes from `Union[Enrollment, None, bool]` to
plain `Enrollment`, and the type is finally a promise rather than a shrug: if
this call returns, the student is in.

**3. core — the two schemas, in `schemas.py`**

`CreateCourseRequest` and `CourseResponse` above them are given. Read them
first: they answer most of the questions, including how to say "this string may
not be empty".

`CreateEnrollmentRequest` — what a client sends:

| Field | Type | Notes |
|---|---|---|
| `course_id` | `str` | may not be empty |
| `student_id` | `str` | may not be empty |
| `name` | `str` | may not be empty |
| `email` | `str` | |
| `has_payment_method` | `bool` | defaults to `False` — a client that says nothing has not said yes |

`EnrollmentResponse` — what the API hands back: `enrollment_id`, `course_id`,
`student_id`, `status`, all `str`. Notice what is *not* there: the student's
email came in on the request and does not go out on the response. Deciding that
is what a separate response model is for.

**4. optional — a field validator on `email`**

Pydantic has already checked that the value is a string; your check runs after
that. Reject the value by raising `ValueError` with a message a human can read.
No test covers this one.

## Check your work

```
python workshop.py test 3
```

**Done when:**

- [ ] `python workshop.py test 3` is green
- [ ] stages 0, 1 and 2 are still green
- [ ] `enroll_student` is annotated `-> Enrollment` and contains no
      `return None` and no `return False`
- [ ] `grep -rn "TODO \[stage-3\]" src/` shows only the optional task, if you
      skipped it

## Common mistakes

- **Forgetting `super().__init__(message)`.** The exception still works, but
  `str(error)` is empty, and in stage 4 that empty string is what the client
  receives as `detail`.
- **Putting the data only in the message.** `raise CourseNotFoundError("course
  python-basics not found")` reads fine and fails the test, which asks for
  `error.course_id`. An exception is a value: give it fields.
- **Logging after the raise.** Nothing after `raise` runs.
- **Reusing one model for request and response.** Then every field a client may
  send is also a field you are obliged to hand back — including the email.
- **Mentioning HTTP in `errors.py`.** No status codes here. Stage 4 has exactly
  one file where a domain error and a status code are allowed to meet.

Stuck? `python workshop.py hint 3`.
