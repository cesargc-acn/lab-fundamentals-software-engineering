# Optional extension · Mutation testing

*Outside the lab budget. Do this if you finished early, or after the session.*

## The question it answers

A green test suite tells you that your tests pass. It does not tell you that
your tests would have caught the bug. Coverage does not answer that either: a
test that calls a function and asserts nothing covers every line in it.

Mutation testing asks the only question that matters. Break the code on purpose,
run the suite, and see whether anything turns red. A change nothing notices is
called a *surviving mutant*, and it is a hole in your suite shaped exactly like
the bug that will eventually go to production through it.

## Run it

Finish stages 2 and 3 first, or every mutant will die for the wrong reason.

```
python workshop.py mutants
```

Three mutants live in `extensions/mutants/`. Each one is the reference
`EnrollmentService` with exactly one behaviour removed:

| Mutant | What it does |
|---|---|
| `mutant_a.py` | ignores the enrollment policy, so a full course keeps taking students |
| `mutant_b.py` | never raises `StudentAlreadyEnrolledError`, so a student can enroll twice |
| `mutant_c.py` | never notifies the student |

They are generated from the reference implementation by
`tools/build_snapshots.py`, so they cannot drift away from the code they are
sabotaging.

## The exercise

The suite you were given kills all three. That is not the interesting part.

1. Comment out `test_the_same_student_cannot_take_two_seats` and run the
   mutants again. `mutant_b` now survives. You have just measured what that one
   test was worth, in a way coverage never could.
2. Do the same with the notification assertions. Notice how many of your tests
   exercise the notifier and how few actually check it.
3. Write a fourth mutant of your own. Change something small and plausible — an
   `<` for a `<=`, an argument order, a `return` moved one line up. If your
   suite does not kill it, you have found a test worth writing.

## In a real project

Nobody writes mutants by hand. [`mutmut`](https://mutmut.readthedocs.io/) and
[`cosmic-ray`](https://cosmic-ray.readthedocs.io/) generate hundreds of them and
report a mutation score. They are slow — every mutant is a full test run — so
they belong on a nightly job rather than in the loop you run while coding.

## Theory reference

Block 11.
