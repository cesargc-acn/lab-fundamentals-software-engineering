# Stage 5 · Async: when and why

**Files you will touch:** the bottom of
`src/course_booking/services/enrollment_service.py`, below the
`Stage 5` banner comment.
**Run the tests with:** `python workshop.py test 5`

---

## New ideas in this stage

**Coroutine.** Calling an `async def` function does not run it. It hands you a
coroutine object. Nothing happens until somebody awaits it.

```python
result = charge(...)          # a coroutine object. Nobody has been charged.
result = await charge(...)    # now it runs, and `result` is the answer.
```

Python does not warn you about the first line. It is a perfectly legal
expression.

**Event loop.** The scheduler that runs all your coroutines on one thread. It
can only switch to other work at an `await`. So:

```python
async def slow():
    time.sleep(0.3)            # blocks the whole process for 0.3 s
                               # no other request runs. Nothing runs.

async def polite():
    await asyncio.sleep(0.3)   # hands control back; other work runs meanwhile
```

Both functions take 0.3 seconds on their own. Five of the first take 1.5
seconds; five of the second take 0.3. `async def` never made anything
concurrent — handing control back did.

**`asyncio.gather`.** Starts several coroutines at once and waits for all of
them. `await` in a loop is right only when each call needs the previous
answer.

Anything else the statement uses is in [GLOSSARY.md](../GLOSSARY.md).

## The problem

Nothing you have written so far waits for anything. A dict lookup returns
immediately, a policy returns immediately, so turning the service into
`async def` would add a keyword to every call site and buy nothing at all.

`payments.py` is the exception: `PaymentGateway.charge` takes about a third of
a second, the way a call over the network does. That is what async is for, and
it is also where async goes wrong in two very specific ways.

## What you will build

Two fixes to code that is already written and already broken. Both bugs are the
kind that pass code review, because the code *looks* asynchronous.

## Your tasks

**1. core — the blocking call, in `charge_enrollment`**

```python
time.sleep(SETTLEMENT_DELAY_SECONDS)
```

Read that line the way the event loop reads it. While it waits, nothing else in
the process runs: not the other four charges, not the health check, nothing.
Five concurrent charges take about 1.8 seconds instead of 0.6.

There is an awaitable version of that call. Use it. The delay must still
happen, and the charge after it must still reach the gateway.

**2. core — the forgotten `await`, in `payment_summary`**

```python
result = charge_enrollment(gateway, student_id, amount)
```

`charge_enrollment` is an `async def`, so this line hands you a coroutine, not
a result, and nobody tells you. The next line happily formats that coroutine
object into a string, the API answers `200`, and the client is told the payment
succeeded. Nobody was charged.

Run `python workshop.py run`, `POST /enrollments/payment` from `/docs`, and
read the response body before you fix it. Seeing
`payment: <coroutine object ...>` go out over HTTP is the point of this task.

**3. optional — `charge_many`**

The loop awaits each charge before starting the next, so independent charges
take turns. Start them all, then wait once. No test covers this one: time the
two versions yourself.

## Check your work

```
python workshop.py test 5
```

Two of these tests hold a stopwatch, with room to spare: five charges of 0.3 s
finish in about 0.6 s when they overlap and about 1.8 s when they queue, and
the threshold sits at 0.9 s. If a timing test fails, it is not your laptop —
the margin is more than double.

**Done when:**

- [ ] `python workshop.py test 5` is green
- [ ] the whole suite is green: `python workshop.py test`
- [ ] you have written down your answer to the question below

## One question, no code

`EnrollmentService` is still synchronous, and the last test in the file
(`test_the_enrollment_service_is_still_synchronous`) insists that it stays that
way. Why is that right, when the API it sits behind is asynchronous?

Write your answer in one sentence before you read
`solutions/stage-05/NOTES.md`. The habit of making everything `async` "to be
safe" is a more expensive mistake than either of the two bugs you just fixed,
and the reasoning is the whole reason this stage exists.

## Common mistakes

- **Deleting the sleep instead of awaiting it.** The tests pass and you have
  removed the thing the exercise is about. The settlement delay is meant to
  stay; it is meant to stop blocking.
- **Adding `async` to `enroll_student` while you are in the file.** The last
  test fails on purpose, and the reasoning question above is why.
- **Fixing `payment_summary` by making it synchronous.** You cannot: awaiting
  requires an `async def`. Reach for `asyncio.run` inside a route and you have
  a loop running inside a loop.
- **Expecting `asyncio.gather` to be faster for dependent calls.** It is not.
  If call two needs the answer to call one, a loop is correct and `gather` is
  wrong.

Stuck? `python workshop.py hint 5`.
