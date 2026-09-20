# Course Booking API — hands-on lab

You are handed a working enrollment system that nobody wants to touch: one
function, ninety lines, validation and business rules and email formatting all
in the same place.

Over five stages you will rebuild it into a FastAPI application with a domain layer,
injected dependencies, named errors and one honest use of async — without ever
breaking the tests that pin down what the old code does.

## Before you start

**You need to be comfortable with:** writing Python functions and classes,
running a command in a terminal, and reading a stack trace.

**You do not need to know:** FastAPI, Pydantic, `typing.Protocol`, dependency
injection, the repository pattern, or `asyncio`. Each stage teaches the piece
it needs, and every term the statements use is defined in
[GLOSSARY.md](GLOSSARY.md) — keep that page open in a second tab.

Nothing you write here is thrown away. Each stage starts from the code the
previous one left behind, so **do the stages in order**: stage 3 tests call the
service you write in stage 2.

## What is in the repository

```
workshop.py                     the only command you run. setup, test, run, hint
README.md                       this page
GLOSSARY.md                     every term the statements use, defined
stages/                         the five statements. Read one before you code
tests/                          the tests. You never edit these
solutions/                      one finished version per stage, plus NOTES.md
src/course_booking/             your code. Every TODO lives here
├── legacy_booking.py           the code you start from. Leave it alone
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

1. Get the code:

   ```
   git clone <REPOSITORY-URL>
   cd lab-fundamentals-software-engineering
   ```

2. Create a virtual environment with Python 3.10 or newer, and activate it:

   ```
   python -m venv .venv
   .venv\Scripts\activate           # Windows
   source .venv/bin/activate        # macOS and Linux
   ```

   You will know it worked because your prompt now starts with `(.venv)`.
   If you open a new terminal later, activate it again.

3. Install and check everything, from the repository root:

   ```
   python workshop.py setup
   ```

   It installs the four dependencies and checks them. It prints `PASS`, or it
   prints the one thing that is wrong and the command that fixes it.

4. Confirm the starting point is green:

   ```
   python workshop.py test 0
   ```

   Those tests pass before you write anything. If they do not, stop and fix the
   setup — everything after this assumes they are green.

### When setup goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `No module named fastapi` | the virtual environment is not active, or `setup` was never run | activate `.venv`, then `python workshop.py setup` |
| `No module named course_booking` | you are not in the repository root | `cd` to the folder that contains `workshop.py` |
| `python: command not found` | your system spells it `python3` | use `python3` everywhere in this page |
| `this workshop needs Python 3.10 or newer` | the venv was built with an old interpreter | delete `.venv`, then `python3.12 -m venv .venv` |
| pip cannot reach the index | corporate proxy | `pip install -r requirements.txt --index-url https://pypi.org/simple` |

## How to work

Five stages. Read the statement first, then open the file, then write code,
then run the tests. Repeat until green.

| Stage | Statement | Run its tests |
|---|---|---|
| 1 · Domain and enrollment policy | [stages/01-domain-and-policy.md](stages/01-domain-and-policy.md) | `python workshop.py test 1` |
| 2 · Repository and dependency injection | [stages/02-repository-and-injection.md](stages/02-repository-and-injection.md) | `python workshop.py test 2` |
| 3 · Domain errors and validation | [stages/03-errors-and-validation.md](stages/03-errors-and-validation.md) | `python workshop.py test 3` |
| 4 · FastAPI: routes, Depends and HTTP codes | [stages/04-fastapi-routes-and-errors.md](stages/04-fastapi-routes-and-errors.md) | `python workshop.py test 4` |
| 5 · Async: when and why | [stages/05-async-when-and-why.md](stages/05-async-when-and-why.md) | `python workshop.py test 5` |

### Finding the work

Every place you have to write something is marked with a comment that names its
stage and its number, and the number matches the statement:

```
# TODO [stage-2] 3 (core): Keep the courses somewhere. A dict keyed by course
#     id is enough, and it makes `get_by_id` a one-liner.
```

`core` tasks are covered by tests and are what "done" means.
`optional` tasks have no test; do them if you have time, skip them without
guilt if you do not.

To see everything a stage still expects from you:

```
grep -rn "TODO \[stage-2\]" src/               # macOS, Linux
findstr /s /n /c:"TODO [stage-2]" src\*.py     # Windows
```

Until you fill one in, the code raises `NotImplementedError("TODO [stage-2] 3")`
— so a failing test that says exactly that is telling you which TODO is next,
not that something is broken.

### Reading a test failure

The tests are the contract, and their failure messages are written to be read.
A run looks like this:

```
FAILED tests/test_stage1_policies.py::test_a_free_course_always_says_yes[2]
E   AssertionError: FreeEnrollmentPolicy refused a student on a free course
E   with 2 enrolled. The legacy code does not count seats on free courses,
E   and neither should this policy.
```

Three things to take from it: the file, the test name (it says what was
expected in words), and the message under `AssertionError` (it says what went
wrong and usually what to do). The `[2]` at the end is the input that failed —
the same test ran over several values and this is the one that broke.

Useful variations, all of which the workshop script prints for you before it
runs them, so you can type them yourself:

```
pytest -m stage1                                 every test of stage 1
pytest -m stage1 -k free                         only the ones with "free" in the name
pytest -m stage1 -x                              stop at the first failure
pytest tests/test_stage1_policies.py -q          one file, quiet output
```

### A stage is done when its tests are green

Not when your code looks like the reference. There are several correct ways to
solve most of these tasks, and the tests are deliberately written so that they
never inspect *how* you did it.

Stage 0 deserves a special mention: `python workshop.py test 0` is green before
you write anything, and it must stay green to the very end. Those tests
describe what the legacy code does, and everything you build has to keep
agreeing with them. That is the whole idea of refactoring under a safety net.

### Other commands

```
python workshop.py hint 3     text hints for one stage. Ideas, never code
python workshop.py run        start the API, then open http://127.0.0.1:8000/docs
python workshop.py test       the whole suite. Only fully green at the very end
```

Every command prints the real tool invocation before running it, so you can
always type that command yourself instead.

## When you get stuck

In this order, and there is no shame in reaching step 4:

1. **Re-read the failing test.** It names the behaviour it wants in its own
   name and explains the failure in its message.
2. **Run `python workshop.py hint <stage>`.** Short nudges towards the idea,
   with no code in them.
3. **Read the theory reference** at the bottom of the stage statement.
4. **Open `solutions/stage-0N/`** and compare. Reading a solution you then
   retype and understand beats staring at a blank file for forty minutes.

## Solutions

Each stage has a reference implementation under `solutions/`. It is one way to
solve it, not the only one. Look at it whenever you want: to compare it with
your own version, to get unstuck, or to move on to the next stage if you would
rather not stay blocked.

`solutions/stage-03/` is the whole project as it stands at the end of stage 3 —
runnable, with the stages after it still marked TODO. Each one also has a
`NOTES.md` explaining the decisions the code does not explain, and saying which
other answers are equally correct. That last section is usually worth more than
the code next to it.

## Pace

The times on each statement are a rough guide for somebody who has seen the
ideas before. Taking twice as long the first time is normal and is not a
signal about you.

There is no mark and nothing to hand in. Reaching stage 3 having understood it
is worth more than reaching stage 5 by copying, and if a stage is not clicking,
reading `solutions/` and moving on is a legitimate way to spend the time.
