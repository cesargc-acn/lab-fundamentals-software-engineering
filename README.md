# Course Booking API — hands-on lab

You are handed a working enrollment system that nobody wants to touch: one function, ninety lines, validation and business rules and email formatting all in the same place.

Over five stages you rebuild it into a FastAPI application with a domain layer, injected dependencies, named errors and one honest use of async — without ever breaking the tests that pin down what the old code does.

```
src/course_booking/
├── legacy_booking.py           the code you start from
├── payments.py                 a slow external call, for stage 5
├── notifications.py            sending, and a fake for tests
├── domain/
│   ├── models.py               Course, Student, Enrollment, Instructor
│   ├── policies.py             stage 1
│   └── errors.py               stage 3
├── repositories.py             stage 2
├── services/enrollment_service.py   stages 2, 3 and 5
├── schemas.py                  stage 3
├── api/
│   ├── dependencies.py         stage 4
│   └── routers/                stage 4
└── main.py                     stage 4
```

## Setup

```
git clone <REPOSITORY-URL>
cd lab-fundamentals-software-engineering
```

Create a virtual environment. Python 3.10 or newer.

```
python -m venv .venv
.venv\Scripts\activate           # Windows
source .venv/bin/activate        # macOS and Linux
```

Then, from the repository root:

```
python workshop.py setup
```

It installs the four dependencies and checks them. It prints `PASS`, or it prints the one thing that is wrong and the command that fixes it.

## How to work

Five stages:

| Stage | Statement | Run |
|---|---|---|
| 1 · Domain and enrollment policy | [stages/01-domain-and-policy.md](stages/01-domain-and-policy.md) | `python workshop.py test 1` |
| 2 · Repository and dependency injection | [stages/02-repository-and-injection.md](stages/02-repository-and-injection.md) | `python workshop.py test 2` |
| 3 · Domain errors and validation | [stages/03-errors-and-validation.md](stages/03-errors-and-validation.md) | `python workshop.py test 3` |
| 4 · FastAPI: routes, Depends and HTTP codes | [stages/04-fastapi-routes-and-errors.md](stages/04-fastapi-routes-and-errors.md) | `python workshop.py test 4` |
| 5 · Async: when and why | [stages/05-async-when-and-why.md](stages/05-async-when-and-why.md) | `python workshop.py test 5` |

Start with `python workshop.py test 0`. It is green before you write anything, and it stays green to the end: those tests describe what the legacy code does, and everything you build has to keep agreeing with them.

The tests are the contract. Every TODO in `src/` is marked with the stage it belongs to, and a stage is done when its tests are green — not when your code looks like the reference. Grep for what is left:

```
grep -rn "TODO \[stage-2\]" src/
```

Other commands:

```
python workshop.py hint 3     text hints for one stage, no code
python workshop.py run        start the API, then open http://127.0.0.1:8000/docs
python workshop.py test       the whole suite, green only at the very end
```

Every command prints the real tool invocation before running it, so you can always type that command yourself instead.

## Solutions

Each stage has a reference implementation under `solutions/`. It is one way to solve it, not the only one. Look at it whenever you want: to compare it with your own version, to get unstuck, or to move on to the next stage if you would rather not stay blocked.

`solutions/stage-03/` is the whole project as it stands at the end of stage 3 — runnable, with the stages after it still marked TODO. Each one also has a `NOTES.md` explaining the decisions the code does not explain, and saying which other answers are equally correct. That last section is usually worth more than the code next to it.

## Pace

There is no mark and nothing to hand in. Reaching stage 3 having understood it is worth more than reaching stage 5 by copying, and if a stage is not clicking, reading `solutions/` and moving on is a legitimate way to spend the time.
