# Optional extension · Server-Sent Events

*Outside the lab budget. Do this if you finished early, or after the session.*

## The question it answers

The dashboard wants to show enrollments as they happen. Polling `GET /courses`
every two seconds works, costs a request per client per two seconds, and is
still up to two seconds late. WebSockets solve it and bring a second protocol,
a second set of proxy problems and a connection you have to manage in both
directions.

Server-Sent Events sit in between: one long-lived HTTP response, `Content-Type:
text/event-stream`, the server writes lines, the browser reconnects on its own.
It only goes one way — server to client — which is exactly what a feed of events
needs and nothing more.

## What to build

A `GET /enrollments/stream` route that emits one event per enrollment, and a
stage 5 lesson applied for real: this route genuinely waits, so it genuinely
belongs in an `async def`.

Sketch, in the order it tends to go well:

1. An `asyncio.Queue` that the application publishes to. One per connected
   client, handed out when the stream opens and dropped when it closes.
2. An `EnrollmentCreated` event — the enrollment id, the course id, the student
   id and a timestamp. Publish it from the place that already knows an
   enrollment happened. Deciding where that is, the service or the route, is the
   interesting part of the exercise.
3. An async generator that awaits the queue and yields the SSE wire format:
   `data: {...}\n\n`, one JSON object per event. Send a comment line (`: ping`)
   every fifteen seconds or a proxy will close the connection for you.
4. Hand the generator to `fastapi.responses.StreamingResponse` with
   `media_type="text/event-stream"`.

Then open two terminals: `curl -N http://127.0.0.1:8000/enrollments/stream` in
one, `POST /enrollments` in the other.

## What to watch out for

- A client that disconnects leaves its queue behind. Clean up in a `finally`.
- An unbounded queue is a memory leak wearing a disguise. Give it a `maxsize`
  and decide what dropping an event means.
- Nothing about this survives a second server process. The moment you run two
  workers, the queue has to move out of the process — Redis pub/sub, or a real
  broker — and that is a different conversation.

There is no reference solution and no test for this one.

## Theory reference

Block 8.5.
