# Stage 1 · Domain and enrollment policy

*About 20 minutes.*

## The problem

`legacy_booking.enroll_student` decides who may enroll with a chain of `if/elif` on the course type, wedged between input validation and email formatting. Adding a fourth course type means editing that function, re-reading all of it, and hoping. The rule and the plumbing are the same ninety lines.

## What you will build

- `EnrollmentPolicy`, a protocol: one question, one method.
- Three policies, one per course type, each small enough to read in a breath.
- The same eight decisions the legacy code makes, with no `elif` in sight.

## Your tasks

All of them in `src/course_booking/domain/policies.py`, except the last one.

1. **core** — `EnrollmentPolicy`: declare `can_enroll(course, student) -> bool`. A protocol method has no implementation; `...` is the body. Nothing needs to inherit from it.
2. **core** — `FreeEnrollmentPolicy`: a free course has no gate.
3. **core** — `LimitedCapacityPolicy`: compare seats taken with seats.
4. **core** — `PaidEnrollmentPolicy`: a seat *and* a payment method.
5. **optional** — in `src/course_booking/notifications.py`, pull the enrollment message out of the code that formats it inline and give it a name: `build_enrollment_message(course, student)`. No test covers this one.

`CourseTypeEnrollmentPolicy` and `default_enrollment_policy()` are given at the bottom of the file. Read them: they are what turns your three classes into the one policy the rest of the application asks.

## Check your work

```
python workshop.py test 1
```

`test_policies_match_legacy_behaviour` is the one that matters. It runs your policies over the same eight cases the stage 0 tests pin down. Green means the rewrite is faithful.

Stuck? `python workshop.py hint 1`.

## Theory reference

Blocks 2, 3 and 4: the domain layer, dependency inversion, and why a protocol is enough.
