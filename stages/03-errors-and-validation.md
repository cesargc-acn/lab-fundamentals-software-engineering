# Stage 3 · Domain errors and validation

*About 20 minutes.*

## The problem

Your service answers `None` when the course does not exist and `False` when the
enrollment is refused, and there are two different reasons it might be refused.
A caller gets a falsy value and has to guess which of the four things happened.
Nobody checks. Nobody logs. The support ticket says "it didn't work".

## What you will build

- Three named errors under one base class, each carrying the data a caller
  needs.
- A service whose return type is the truth: if it comes back, the student is in.
- Request and response models, so what may cross the wire is written down.

## Your tasks

In `domain/errors.py`, `services/enrollment_service.py` and `schemas.py`.

1. **core** — the constructors of `CourseNotFoundError`,
   `StudentAlreadyEnrolledError` and `EnrollmentNotAllowedError`. `DomainError`
   is given: it is the root that lets one `except` catch the family.
2. **core** — in `enroll_student`, replace the three return-value signals with
   those errors, and call `_log_failure` before each `raise`. `_log_failure` is
   given, and the fields it writes are the ones the theory asks for.
3. **core** — `CreateEnrollmentRequest` and `EnrollmentResponse`.
   `CreateCourseRequest` and `CourseResponse` above them are given: read them
   first, they answer most of the questions.
4. **optional** — a field validator on `email`. No test covers this one.

## Check your work

```
python workshop.py test 3
```

Watch what happens to the signature of `enroll_student` when you are done. It
goes from `Union[Enrollment, None, bool]` to `Enrollment`, and the type is
finally a promise rather than a shrug.

## Theory reference

Blocks 4 and 5: domain errors, validation at the edge, and section 5.6 on
structured logging (`operation`, `error_type`, and the timestamp and level
every record already carries).
