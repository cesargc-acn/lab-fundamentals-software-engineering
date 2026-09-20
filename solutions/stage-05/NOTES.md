# Stage 5 — notes on this implementation

Read this after your own version is green — and, for this stage, after you
have written down your own answer to the question in the statement.

**The short version**

- `async def` is not a performance keyword. It is a promise to hand control
  back, and a blocking call inside one breaks that promise silently.
- Calling a coroutine function without `await` gives you an object, not a
  result, and the only warning is a `RuntimeWarning` nobody reads.
- `asyncio.gather` is for calls that do not depend on each other. Awaiting in
  a loop is correct whenever they do.
- `EnrollmentService` stays synchronous because it never waits for anything,
  and that is the most common async mistake of the three.

## Why this implementation

`time.sleep` inside an `async def` is the mistake this stage exists for. The function is a coroutine, it is awaited correctly, everything looks asynchronous, and the process still stops dead for a third of a second: nothing else runs, not the other four charges, not the health check. `await asyncio.sleep(...)` differs in exactly one way that matters — it hands control back to the event loop, which is the only thing that ever makes anything concurrent. `async def` is not a performance keyword. It is a promise to yield, and a blocking call breaks it.

The missing `await` in `payment_summary` is the quieter failure, and the worse one. Calling a coroutine function gives you a coroutine object; Python does not complain, the string gets built, and the API answers 200 with `payment: <coroutine object ...>` in it. The client is told the payment succeeded. Nobody was charged. The only warning you get is a `RuntimeWarning` on standard error that nobody reads in production.

`charge_many` uses `asyncio.gather` because the charges are independent. That is the entire condition: `await` in a loop is correct whenever the next call needs the last one's answer, and wasteful whenever it does not.

**And the question from the statement.** `EnrollmentService` is still synchronous, and that is right, because it never waits for anything. A dict lookup, a policy call and a notification all return immediately; there is no point at which the event loop could go and do something useful. Making it `async def` would add a keyword to every call site, force every caller into a loop, and buy nothing — that is the mistake in section 8.4, and it is much more common than the two you just fixed. Async is not a quality of good code. It is a tool for code that waits, and FastAPI runs synchronous routes in a thread pool precisely so that this choice stays yours.

## Other valid approaches

If you kept a genuinely blocking call because a library gave you no async version, the right move is `asyncio.to_thread(...)` (or `loop.run_in_executor`), which pushes the blocking work off the event loop instead of pretending it is not blocking. That is the correct fix for a third-party SDK you cannot change.

If you are on Python 3.11 or later, `asyncio.TaskGroup` does what `gather` does with better failure semantics: one task raising cancels the rest instead of leaving them running.

If you built `charge_many` with `asyncio.as_completed` to handle results as they arrive, that is also correct and better when you want to start using the first answer before the last one lands.

## Theory reference

Block 8: the event loop, what `await` actually yields, and section 8.4 on making things `async` that have nothing to wait for.

## If you have spare time

Make `PaymentGateway.charge` fail one time in three, and add a retry with exponential backoff around it. Then run five concurrent charges again and watch what the retries do to the total time. Deciding where that retry belongs — the gateway, the service, or the route — is the interesting part. There is no reference solution for it.
