# Stage 5 · Async: when and why

*About 25 minutes.*

## The problem

Nothing you have written so far waits for anything. A dict lookup returns immediately, a policy returns immediately, so turning the service into `async def` would add a keyword to every call site and buy nothing at all. `payments.py` is the exception: `PaymentGateway.charge` takes about a third of a second, the way a call over the network does. That is what async is for, and it is also where async goes wrong in two very specific ways.

## What you will build

Two fixes to code that is already written and already broken, at the bottom of `services/enrollment_service.py`.

## Your tasks

1. **core** — `charge_enrollment` waits for the settlement window with a blocking call inside an `async def`. Five concurrent charges take about 1.8 seconds instead of 0.6. `async def` never made anything concurrent; handing control back does, and that line never hands anything back.
2. **core** — `payment_summary` calls an `async def` and never awaits it. The line runs, the string gets built, the payment never happens, and the client is told everything is fine. Read the response body to see what went out.
3. **optional** — `charge_many` makes independent charges take turns. Start them all, wait once. No test covers this one: time the two versions yourself.

## Check your work

```
python workshop.py test 5
```

Two of these tests hold a stopwatch, with room to spare: five charges of 0.3 s finish in about 0.6 s when they overlap and about 1.8 s when they queue, and the threshold sits at 0.9 s.

## One question, no code

`EnrollmentService` is still synchronous, and the last test in the file insists that it stays that way. Why is that right, when the API it sits behind is asynchronous? Write your answer down in one sentence before you read `solutions/stage-05/NOTES.md`.

## Theory reference

Block 8: the event loop, what `await` actually yields, and section 8.4 on making things `async` that have nothing to wait for.
