# Stage 2 · Repository and dependency injection

**Files you will touch:** `src/course_booking/repositories.py`,
`src/course_booking/services/enrollment_service.py`, and `notifications.py` for
the optional task.
**Run the tests with:** `python workshop.py test 2`
**If stage 1 never went green:** start this one from `solutions/stage-01/`
rather than staying blocked — [Solutions](../README.md#solutions) says how.

---

## New ideas in this stage

**Repository.** An object that hides *where* data is kept behind the questions
a caller wants answered. The caller says "give me the course with this id", not
"run this query" — so the day the dict becomes a database, the caller does not
change.

**Dependency injection.** A class is handed the things it needs instead of
building them itself. That is the whole difference, and it is one line:

```python
class Bad:
    def __init__(self) -> None:
        self._repo = InMemoryCourseRepository()   # decided here, forever

class Good:
    def __init__(self, repo: CourseRepository) -> None:
        self._repo = repo                         # decided by whoever builds it
```

`Bad` can only ever be tested against the real storage. `Good` can be handed
anything with the right methods, which is exactly what the last test of this
stage does.

Both terms, and anything else the statement uses, are in
[GLOSSARY.md](../GLOSSARY.md).

## The problem

The legacy code keeps its data in module-level dictionaries: `COURSES`,
`ENROLLMENTS`, `SENT_EMAILS`. You have already met the consequence, even if you
did not notice it — open `tests/conftest.py` and look at `reset_legacy_state`.
It has to put those three dictionaries back the way they were before *every
single test*, or one test decides what the next one sees.

There is also no way to run that code against anything else, because "anything
else" was never a thing it could be handed.

## What you will build

- Two protocols written from the caller's side: what the service needs to ask.
- One implementation of each, backed by dictionaries.
- `EnrollmentService`, which receives its four collaborators and builds none.

## Your tasks

Tasks 1 to 3 are in `repositories.py`, task 4 in
`services/enrollment_service.py`, task 5 in `notifications.py`.

**1. core — the `CourseRepository` protocol**
Three methods, no bodies (`...` each):

```python
def get_by_id(self, course_id: str) -> Optional[Course]: ...
def list_available_courses(self) -> List[Course]: ...
def save(self, course: Course) -> None: ...
```

**2. core — the `EnrollmentRepository` protocol**
Two methods, same treatment:

```python
def save(self, enrollment: Enrollment) -> None: ...
def exists_for(self, course_id: str, student_id: str) -> bool: ...
```

`exists_for` answers a yes/no question, so it returns a `bool` rather than an
object the caller has to inspect.

**3. core — `InMemoryCourseRepository` and `InMemoryEnrollmentRepository`**
A dict keyed by id is enough for both. Four rules the tests check:

- `get_by_id` returns `None` for an id it does not know. It does not raise.
- `save` replaces what is stored under the same id; saving twice does not
  create two courses.
- `list_available_courses` returns, **sorted by course id**, the courses a
  student could still join: a course is joinable when it is free, or when it
  still has a seat left.
- **Hand out copies, not the stored objects.** `dataclasses.replace(course)` is
  already imported for this. A caller that changes what `get_by_id` gave it
  must not change what is stored until it calls `save` — that is how a real
  database behaves, and the test
  `test_what_get_by_id_returns_is_not_what_is_stored` insists on it.
  `Enrollment` is frozen, so there is nothing to copy on that side.

**4. core — `EnrollmentService.__init__` and `enroll_student`**

The constructor stores the four collaborators it is given and does nothing
else. No `import` of a concrete repository, no `InMemory...()` call anywhere
inside the service — whoever built the service already chose the
implementations, and that is the whole point of the stage.

`enroll_student(course_id, student)` is the use case, in the order the
whiteboard has it:

1. find the course
2. refuse a student who already holds a seat
3. ask the policy whether this student may enroll
4. build an `Enrollment` (a `str(uuid4())` makes a fine id)
5. save the enrollment
6. add one to the course's `enrolled_count`
7. save the course back
8. notify the student
9. return the enrollment

For the three refusals, signal failure the way the legacy code does, by
returning:

| Refusal | Return |
|---|---|
| no course with that id | `None` |
| the student already holds a seat | `False` |
| the policy says no | `False` |

Then read the return type you ended up needing:
`Union[Enrollment, None, bool]`. A caller gets a falsy value back and has to
guess which of three things happened. Sit with that for a second — stage 3 is
where it is paid back.

Nothing at all may happen after a refusal: no enrollment saved, no seat taken,
no notification sent.

**5. optional — `create_notification_sender(channel)` in `notifications.py`**
One function, one branch, returning a `NotificationSender` for the channel
name `"email"` or `"fake"`. The caller asks for a channel and never learns
which class it got. No test covers this one.

## Check your work

```
python workshop.py test 2
```

`test_the_service_does_not_care_which_repository_it_got` is the one that
matters. It swaps `InMemoryCourseRepository` for `ListCourseRepository` — a
completely different implementation, backed by a list, defined at the top of
the test file — and expects the service to behave identically. If it passes,
nothing in the service knows how the data is stored. That is the whole return
on this stage.

**Done when:**

- [ ] `python workshop.py test 2` is green
- [ ] `python workshop.py test 0` and `test 1` are still green
- [ ] `grep -n "InMemory" src/course_booking/services/enrollment_service.py`
      finds nothing
- [ ] `grep -rn "TODO \[stage-2\]" src/` shows only the optional task, if you
      skipped it

## Common mistakes

- **Storing the object instead of a copy.** Everything passes except the two
  tests about copies, and the failure looks spooky: a value you never saved has
  changed.
- **Forgetting step 7.** If you increment `enrolled_count` but never call
  `courses.save(course)`, the seat is taken on your local copy and nowhere
  else. `test_enrolling_takes_a_seat_on_the_course` catches exactly this.
- **Notifying before the refusal checks.** A refused student who gets a
  congratulations email is worse than no email at all.
- **Building a repository inside the service.** The stage-2 tests would still
  pass; the swap test at the bottom would not.
- **Renaming the constructor parameters.** The tests build the service with
  keyword arguments: `EnrollmentService(courses=..., enrollments=...,
  policy=..., notifier=...)`. Keep those four names.

Stuck? `python workshop.py hint 2`.
