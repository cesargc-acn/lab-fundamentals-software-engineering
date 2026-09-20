# Glossary

Every term this lab uses, in plain words, with the place in the repository
where you meet it. You do not have to read this page end to end. Come back to
it the moment a stage statement uses a word you would not be able to explain to
somebody else.

---

## Architecture words

**Domain**
The part of the code that talks about courses, students and enrollments — the
things the business cares about. It does not know that an HTTP server exists,
that data lives in a dict, or that anything is sent by email.
*In this repo:* `src/course_booking/domain/`.

**Domain layer / layers**
A way of splitting a program into rings. The inner ring (the domain) holds the
rules. The outer rings (HTTP, storage, email) hold the plumbing. The rule is
that the arrows only point inwards: the domain never imports the API, the API
imports the domain.
*In this repo:* `domain/` is the inner ring, `api/` is the outer one, and
`services/` sits between them.

**Entity**
An object the domain reasons about, with an identity of its own. A `Course`
with `course_id="python-basics"` is the same course tomorrow even if its title
changes.
*In this repo:* `domain/models.py`.

**Use case / service**
One complete thing the application can do, written as a sequence of steps.
"Enroll a student on a course" is a use case; it is not a rule, not a route and
not a database query — it is the orchestration of all three.
*In this repo:* `EnrollmentService.enroll_student`.

**Composition root**
The single place in a program where you choose the concrete classes: "the
course repository is the in-memory one, the notifier is the email one". Keeping
that decision in one file is what lets every other file depend on descriptions
instead of on classes.
*In this repo:* `api/dependencies.py`.

---

## Protocols and dependency injection

**Protocol** (`typing.Protocol`)
A written-down list of the methods a caller is allowed to ask for. Any object
that happens to have those methods satisfies it — there is no `class Foo(Bar)`
to write, and the object never learns the protocol exists. This is Python's
version of "duck typing, but checkable".

```python
from typing import Protocol

class Greeter(Protocol):
    def greet(self, name: str) -> str:
        ...          # a protocol declares, it does not implement

class Spanish:       # notice: it does not inherit from Greeter
    def greet(self, name: str) -> str:
        return "Hola, %s" % name

def welcome(greeter: Greeter) -> str:   # asks for the shape, not the class
    return greeter.greet("Ada")
```

*In this repo:* `EnrollmentPolicy`, `CourseRepository`, `EnrollmentRepository`,
`NotificationSender`.

**Interface**
The same idea under its language-neutral name. In Java you would write
`interface`; in Python a `Protocol` does the job, and an abstract base class
(`abc.ABC`) is the heavier alternative.

**Dependency injection**
A class is *handed* the things it needs instead of building them itself. The
difference is one line, and it is the whole of stage 2:

```python
class Bad:
    def __init__(self):
        self.repo = InMemoryCourseRepository()   # decided here, forever

class Good:
    def __init__(self, repo: CourseRepository):
        self.repo = repo                         # decided by whoever calls it
```

The payoff is that a test can hand `Good` a different repository without
changing a line of `Good`.

**Constructor injection**
Dependency injection done through `__init__`, which is the version this lab
uses. The alternatives (setting attributes afterwards, passing collaborators to
each method) exist, but this one makes it impossible to build a half-wired
object.

**Dependency inversion**
The rule behind the trick above: both the service and the repository depend on
the *protocol*, and neither depends on the other. Before: service → concrete
repository. After: service → protocol ← concrete repository. The arrow into the
detail has been inverted.

**Collaborator**
Any object a class is given to do its job. `EnrollmentService` has four:
a course repository, an enrollment repository, a policy and a notifier.

---

## Patterns you will implement

**Repository**
An object that hides where data is kept behind questions the caller wants
answered — `get_by_id`, `save`, `list_available_courses`. It never exposes
"run this query", because that would tie the caller to one kind of database
forever.
*In this repo:* `repositories.py`.

**Policy** (also: strategy)
One business rule, extracted into its own small object, so that choosing
between rules becomes choosing between objects instead of writing `elif`.
*In this repo:* `FreeEnrollmentPolicy`, `LimitedCapacityPolicy`,
`PaidEnrollmentPolicy`.

**Composite**
An object that satisfies a protocol by delegating to other objects that satisfy
the same protocol. Callers cannot tell the difference between one rule and a
bag of rules.
*In this repo:* `CourseTypeEnrollmentPolicy` picks a policy by course type and
is itself a policy.

**Factory**
A function whose job is to build and return an object, so the caller can ask
for "an email sender" without naming a class.
*In this repo:* `default_enrollment_policy()`, and the optional
`create_notification_sender(channel)`.

---

## Errors, validation and logging

**Domain error**
An exception that names something the business refuses to do —
`CourseNotFoundError`, not `KeyError`. It carries the data a caller needs
(which course, which student) as attributes, so nobody has to parse a message.
*In this repo:* `domain/errors.py`.

**Base exception class**
A common parent (`DomainError`) that lets one `except DomainError:` catch the
whole family, while a caller who cares about one specific failure can still
catch just that one.

**Schema** (in the Pydantic sense)
A class that describes the shape of data crossing the boundary of your
application: what a client may send in, what you agree to send back. It is
*not* the entity. `Course` is what the domain reasons about; `CourseResponse`
is what a client is allowed to see.
*In this repo:* `schemas.py`.

**Validation at the edge**
Checking that incoming data is well formed as early as possible — in the
schema, before any of your own code runs — so the inside of the application can
assume it is dealing with sane values.

**Field validator**
A function Pydantic runs on one field after the type check passes, to enforce a
rule the type cannot express ("this string must contain an `@`"). You reject a
value by raising `ValueError`.

**Structured logging**
Writing a log line as named fields (`operation="enroll_student"`,
`error_type="CourseNotFoundError"`) instead of as one sentence. Six months
later, somebody can filter by `error_type` without inventing a regular
expression.
*In this repo:* `_log_failure` in `services/enrollment_service.py`.

---

## HTTP and FastAPI

**Route / handler / endpoint**
The function that runs when a request arrives at a path. Three words for the
same thing.

**Router** (`APIRouter`)
A group of related routes kept in one file and plugged into the app with
`app.include_router(...)`.
*In this repo:* `api/routers/courses.py` and `api/routers/enrollments.py`.

**`Depends`**
FastAPI's dependency injection. You declare a parameter whose default is
`Depends(some_function)`, FastAPI calls `some_function()` before your route
runs and passes the result in. The route never builds the thing itself, which
is exactly why a test can substitute it.

**`dependency_overrides`**
A dict on the app where a test says "when a route asks for the course
repository, give it this one instead". It only works because the routes ask
with `Depends`.
*In this repo:* the `client` fixture in `tests/conftest.py`.

**Exception handler**
A function registered on the app with `@app.exception_handler(SomeError)`.
When any route raises `SomeError`, FastAPI calls it and sends back whatever it
returns. It is what lets a router raise a domain error and never mention a
status code.
*In this repo:* `main.py`, stage 4.

**Status codes used here**

| Code | Means | Used when |
|---|---|---|
| 200 | OK | a read that found something |
| 201 | Created | `POST` that created a resource |
| 404 | Not Found | `CourseNotFoundError` |
| 409 | Conflict | `StudentAlreadyEnrolledError` — the request fights the state the server is already in |
| 422 | Unprocessable Entity | the request was well formed and was still refused: a bad field, or `EnrollmentNotAllowedError` |

**`lru_cache`**
A decorator that remembers the result of a function. With `maxsize=1` on a
provider that takes no arguments, it means "build it once, hand the same object
to everybody after that" — which is how you get one shared repository per
application.

---

## Async

**Blocking call**
A call that stops the thread until it is done. `time.sleep(1)` blocks.
Inside an `async def`, a blocking call freezes the entire application: no other
request runs for that second.

**Coroutine**
What calling an `async def` function gives you. It is an object, not a result.
Nothing runs until somebody awaits it.

```python
result = charge(...)         # a coroutine object. Nothing has happened.
result = await charge(...)   # now it runs, and `result` is the answer.
```

**`await`**
Runs a coroutine and hands control back to the event loop while it waits, so
other work can run in the meantime. Forgetting it is the bug in stage 5 task 2.

**Event loop**
The scheduler that runs all your coroutines on one thread. It can only switch
to other work at an `await`. That is why an `async def` full of blocking calls
is slower than a plain function: it has promised to yield and never does.

**`asyncio.gather`**
Starts several coroutines at once and waits for all of them. Use it when the
calls are independent; `await` in a loop is right only when each call needs the
previous answer.

---

## Testing

**Characterization test**
A test written against code you did not write, to record what it *currently*
does — bugs included — so you can rewrite it and prove nothing changed. It is
the safety net for a refactor, not a statement about what the code *should* do.
*In this repo:* `tests/test_stage0_characterization.py`, green from the first
minute to the last.

**Refactor**
Changing the shape of code without changing what it does. The "without
changing what it does" part is only credible if tests say so, which is why
stage 0 comes first.

**Fixture** (pytest)
A function marked `@pytest.fixture` that prepares something a test needs. A
test asks for it by naming it as a parameter.
*In this repo:* `sample_course`, `fake_notifier`, `client` and friends, all in
`tests/conftest.py`.

**Fake vs mock**
A *fake* is a real, working, simplified implementation — `FakeNotificationSender`
records messages in a list. A *mock* is a recording object configured to expect
calls. This lab uses fakes everywhere, because a fake is tested by the same
protocol as the real thing and a mock is not.

**Marker** (pytest)
A label on a test, here one per stage (`@pytest.mark.stage3`), which is what
makes `python workshop.py test 3` possible.

**Parametrize**
Running the same test body over a table of inputs, with
`@pytest.mark.parametrize`. One failure per row, so you learn *which* case
broke.
