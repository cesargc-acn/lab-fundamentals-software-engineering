# Stage 1 · Domain and enrollment policy

**Files you will touch:** `src/course_booking/domain/policies.py`, and
`src/course_booking/notifications.py` for the optional task.
**Run the tests with:** `python workshop.py test 1`

---

## New ideas in this stage

**Protocol.** A class that lists the methods a caller is allowed to ask for,
and implements none of them. Any object that happens to have those methods
satisfies it — nothing has to inherit from it, and the object never learns the
protocol exists.

```python
from typing import Protocol

class Greeter(Protocol):
    def greet(self, name: str) -> str:
        ...                       # the body of a protocol method is literally `...`

class Spanish:                    # note: it does NOT inherit from Greeter
    def greet(self, name: str) -> str:
        return "Hola, %s" % name

def welcome(greeter: Greeter) -> str:
    return greeter.greet("Ada")   # asks for the shape, not for a class

welcome(Spanish())                # works
```

**Policy.** One business rule, moved into its own small object, so that picking
between rules becomes picking between objects instead of writing `elif`.

Both terms, and anything else the statement uses, are in
[GLOSSARY.md](../GLOSSARY.md).

## The problem

Open `src/course_booking/legacy_booking.py` and find `enroll_student`. In the
middle of it there is a chain of `if/elif` on the course type, wedged between
input validation above it and email formatting below it. Adding a fourth course
type means editing that function, re-reading all ninety lines of it, and
hoping. The rule and the plumbing are the same function.

## What you will build

- `EnrollmentPolicy`, a protocol: one question, one method.
- Three policies, one per course type, each small enough to read in a breath.
- The same eight decisions the legacy code makes, with no `elif` in sight.

The eight decisions are written down once, as a table, in
`tests/conftest.py` under `LEGACY_DECISIONS`. Read it before you start: it is
the specification for this whole stage.

## Your tasks

Tasks 1 to 4 are all in `src/course_booking/domain/policies.py`, in the order
they appear in the file. Task 5 is in `notifications.py`.

**1. core — `EnrollmentPolicy`**
Declare the single method of the protocol:

```python
def can_enroll(self, course: Course, student: Student) -> bool:
```

Its body is a literal `...`. Nothing needs to inherit from this class.

**2. core — `FreeEnrollmentPolicy.can_enroll`**
A free course has no gate. Read what `legacy_booking.enroll_student` does when
`course["type"] == "free"` and say the same thing in one line. It does not
count seats; neither do you.

**3. core — `LimitedCapacityPolicy.can_enroll`**
Return `True` while there is a seat left, `False` once there is not. The
`Course` object carries both numbers you need — `enrolled_count` and
`capacity` — and also a `seats_left` property if you prefer reading it that
way. Watch the boundary: a course with 2 of 2 seats taken is full.

**4. core — `PaidEnrollmentPolicy.can_enroll`**
A paid course asks two questions, not one: is there a seat left, *and* does the
student have a payment method? Both have to be true. `Student` carries
`has_payment_method`.

**5. optional — `build_enrollment_message` in `notifications.py`**
`legacy_booking` builds the email in the middle of the enrollment logic, and
`EmailNotificationSender` below repeats the trick. Give that message a name and
a home of its own:

```python
def build_enrollment_message(course: Course, student: Student) -> Notification:
```

Then have `EmailNotificationSender.notify_enrollment` call it instead of
formatting strings itself. No test covers this one.

### Already written for you

`CourseTypeEnrollmentPolicy` and `default_enrollment_policy()` are at the
bottom of the file and need no changes. Read them before you run the tests:
they are what turns your three small classes into the single policy the rest of
the application asks. `CourseTypeEnrollmentPolicy` holds a dict of policies,
looks one up by course type, and satisfies `EnrollmentPolicy` itself — which is
why `EnrollmentService` will be able to take one policy and still behave
differently for free, limited and paid courses.

## Check your work

```
python workshop.py test 1
```

Read the failures from the top; the first one usually explains the rest.

`test_policies_match_legacy_behaviour` is the one that matters. It runs your
policies over the same eight cases the stage 0 tests pin down on the legacy
code. Green means the rewrite is faithful.

**Done when:**

- [ ] `python workshop.py test 1` is green
- [ ] `python workshop.py test 0` is still green
- [ ] there is no `if`, `elif` or `course_type` comparison in your three policy
      classes — the choosing happens in `CourseTypeEnrollmentPolicy`
- [ ] `grep -rn "TODO \[stage-1\]" src/` shows only the optional task, if you
      skipped it

## Common mistakes

- **Returning something that is not a `bool`.** The tests use `is True` and
  `is False`, so `return course.seats_left` fails even when the number is
  truthy. Return the comparison itself.
- **Counting seats in `FreeEnrollmentPolicy`.** It looks like an oversight in
  the legacy code, and it may well be one, but stage 0 has pinned it down.
  Faithful first; improvements are a conversation to have with the tests in
  hand.
- **Off by one on capacity.** `enrolled_count < capacity` and
  `enrolled_count <= capacity` differ on exactly the case the test checks.
- **Making the policies inherit from `EnrollmentPolicy`.** Harmless, but it
  misses the point: the whole reason for a protocol is that they do not have
  to.

Stuck? `python workshop.py hint 1`.
