# Stage 2 — notes on this implementation

Read this after your own version is green, or when you are stuck and want to
see one way through. The code next to it is *a* solution, not *the* solution.

**The short version**

- The protocols name the questions the caller asks, never the storage that
  answers them. A protocol saying `execute(sql)` would invert nothing.
- The repositories hand out copies, so that "I changed the object" and "I
  saved the object" stay two different events, exactly as in a database.
- The service takes four collaborators and builds none, which is the only
  reason the swap test at the bottom of the stage can exist.

## Why this implementation

The two protocols are written from the caller's side. `get_by_id`, `list_available_courses` and `exists_for` are the questions the service needs answered; none of them mentions a table, a query or a connection. That is the difference between an interface and a leaked implementation: a protocol that said `execute(sql)` would technically invert the dependency and would still tie the service to a relational database forever.

`InMemoryCourseRepository` hands out copies, both on the way in and on the way out. Without that, a caller holding a `Course` could change what is stored without ever calling `save`, and the day you move to a real database that same code would silently stop working, because a row does not change when the object you loaded from it does. Copying in memory buys you the same rules you will get from a session later.

`EnrollmentService` takes four collaborators and builds none of them. It does call `uuid4()` to mint an enrollment id, which is a hidden dependency: a purist would inject an id generator, and a test that wanted to assert on the id would have to. Nothing here needs that yet, and the trade is worth naming rather than hiding.

One rule ended up in two places: `list_available_courses` decides that a full course is not available, which is very close to what `LimitedCapacityPolicy` decides. That is a real smell, and the honest fix is to ask the policy. It is left alone here because the repository has no policy to ask, which is exactly how this kind of duplication gets in.

## Other valid approaches

If you backed the repositories with a list instead of a dict, that is correct — `test_the_service_does_not_care_which_repository_it_got` builds exactly that and expects the service not to notice.

If you returned the stored object instead of a copy and documented it, that is a defensible choice too, as long as it is a choice. The failure mode is doing it by accident.

If your `enroll_student` checks the policy before the duplicate, the tests pass either way. The order only becomes a decision in stage 3, when each check gets its own error and the caller starts seeing which one fired first.

## Theory reference

Block 3: the repository pattern, constructor injection, and depending on a protocol rather than a class.

## If you have spare time

Add a `StudentRepository`, and change `POST /enrollments` so the request carries only a `student_id` and the router looks the student up. It is a small change with a large question behind it: does the service take a fourth repository, or does the router resolve the student before calling it? Write the tests first; they will tell you which answer you actually believe. There is no reference solution for it.
