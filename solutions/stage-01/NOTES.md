# Stage 1 — notes on this implementation

## Why this implementation

`EnrollmentPolicy` is a `typing.Protocol` and not an abstract base class. An ABC would force every policy to inherit from it, which means the policy has to import the domain before the domain can use the policy. A protocol reverses that: it describes the shape a caller needs, and any object with a matching `can_enroll` satisfies it without knowing the protocol exists. The dependency points from the caller to the description, and never the other way round.

`CourseTypeEnrollmentPolicy` is the piece that keeps `EnrollmentService` down to a single injected policy. It is a policy whose job is to pick a policy, which sounds like a trick and is really just the composite pattern: it satisfies the same protocol, so nothing downstream can tell the difference. An unknown course type is refused rather than raising, because "we have never heard of this course type" is a no, not a crash.

`PaidEnrollmentPolicy` repeats the `enrolled_count < capacity` comparison that `LimitedCapacityPolicy` already makes. That is a deliberate choice of duplication over indirection at this size: two short conditions on one line are easier to read than an object that delegates half of its answer.

## Other valid approaches

If you solved this with a dictionary of functions instead of classes, that is correct. `{"free": lambda course, student: True, ...}` satisfies nothing formally and everything practically, and for rules this small it is arguably the better trade. The tests never ask what kind of object a policy is.

If you made `PaidEnrollmentPolicy` hold a `LimitedCapacityPolicy` and delegate the capacity half of the question to it, that is also correct, and it is the version that ages better the day capacity stops meaning `count < capacity`.

If you gave `Course.course_type` an `Enum` instead of a string, you were right to want to, and the reason it is a string here is that the legacy dictionaries hold strings and stage 0 pins that down.

## Theory reference

Blocks 2, 3 and 4: the domain layer, dependency inversion, and protocols as the cheapest possible interface.

## If you have spare time

Add a fourth policy that only admits students who have completed a previous course, register it in `default_enrollment_policy`, and write its tests. You will find that `can_enroll(course, student)` does not give you enough to answer the question, and what you do about that — widen the protocol, or hand the policy a repository — is the first genuinely architectural decision in this project. There is no reference solution for it.
