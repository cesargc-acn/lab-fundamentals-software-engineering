# Stage 2 · Repository and dependency injection

*About 20 minutes.*

## The problem

The legacy code keeps its data in a module-level dictionary. You have already
met the consequence: `tests/conftest.py` has to reset that dictionary before
every single test, or one test decides what the next one sees. There is no way
to run it against anything else, because "anything else" was never a thing it
could be handed.

## What you will build

- Two protocols written from the caller's side: what the service needs to ask.
- One implementation of each, backed by dictionaries.
- `EnrollmentService`, which receives its four collaborators and builds none.

## Your tasks

In `src/course_booking/repositories.py` and
`src/course_booking/services/enrollment_service.py`.

1. **core** — `CourseRepository`: `get_by_id`, `list_available_courses`, `save`.
2. **core** — `EnrollmentRepository`: `save`, `exists_for`.
3. **core** — `InMemoryCourseRepository` and `InMemoryEnrollmentRepository`.
   Hand out copies, not the stored objects.
4. **core** — `EnrollmentService.__init__` and `enroll_student`. The
   constructor stores what it is given: no `import` of a concrete repository,
   no `InMemory...()` call anywhere inside the service.
5. **optional** — `create_notification_sender(channel)` in
   `notifications.py`. No test covers this one.

For now, signal the three failures the way the old code does, by returning.
Look at the return type you end up needing. Stage 3 is where that is paid back.

## Check your work

```
python workshop.py test 2
```

The last test swaps `InMemoryCourseRepository` for a completely different
repository backed by a list, and expects the service to behave identically. If
it passes, nothing in the service knows how the data is stored. That is the
whole return on this stage.

## Theory reference

Block 3: the repository pattern, constructor injection, and depending on a
protocol instead of a class.
