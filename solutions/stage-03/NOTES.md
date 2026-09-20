# Stage 3 — notes on this implementation

Read this after your own version is green, or when you are stuck and want to
see one way through. The code next to it is *a* solution, not *the* solution.

**The short version**

- An exception is a value: give it fields, so a handler never parses a
  message to find out which course was missing.
- `DomainError` exists only so one `except` can catch the family.
- Request and response models are separate classes because what a client may
  send and what you are obliged to return are different lists.
- The log line names `operation` and `error_type` as fields, not as prose,
  because that is what makes six months of logs filterable.

## Why this implementation

Each error carries the ids it is about, not just a formatted sentence. The handler in `main.py` could parse a message to find out which course was missing, and it would break the first time somebody improved the wording. An exception is a value: give it fields.

`DomainError` exists so that a caller who does not care which of the three failures happened can write one `except` and mean it, while a caller who does care can still catch the specific one. That is the only reason for a base class here — it has no behaviour of its own, and it does not need any.

The log line is written where the failure is understood, which is the service, and it names the operation and the error type as separate fields rather than baking them into the message. The record already carries the timestamp and the level; repeating them would just be two more ways to disagree with the logging library. Structured fields are what let someone filter six months of logs by `error_type` without writing a regular expression.

Request and response models are separate classes on purpose. `CreateEnrollmentRequest` accepts an email, `EnrollmentResponse` does not return one. If a single model did both, every field a client is allowed to send would also be a field the API is obliged to hand back.

## Other valid approaches

If you wrote a single `EnrollmentError` with a `code` field instead of three classes, that is a real design used in real systems, and it trades a bigger `except` surface for a smaller class count. The cost shows up in stage 4: the handler stops being three small functions and becomes one function with a mapping in it.

If you built the message inside the handler instead of inside the exception, the tests still pass. The reason it lives in the exception here is that the service already knows everything needed to write it, and the handler would have to be told.

`pydantic.EmailStr` would validate the address properly. It is not used here because it needs `email-validator`, and this workshop has four dependencies and no fifth.

## Theory reference

Blocks 4 and 5: domain errors, validating at the edge, and section 5.6 on structured logging.

## If you have spare time

Give `EnrollmentResponse` a `from_enrollment` classmethod, the way `CourseResponse` has `from_course`, and see whether the router reads better for it. Then add a correlation id to `_log_failure` and thread it through from the request, so two log lines from the same call can be found together. There is no reference solution for either.
