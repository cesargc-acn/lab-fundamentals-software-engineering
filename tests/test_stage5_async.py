"""Stage 5. The one place in the project where async earns its keep.

Two of these tests hold a stopwatch. The margins are wide on purpose: five
charges of 0.3 s each take about 0.6 s when they overlap and about 1.8 s when
they do not, and no laptop is slow enough to confuse those two numbers.

There is no pytest-asyncio here. `asyncio.run` is enough, and it keeps what is
being measured in plain sight.
"""

from __future__ import annotations

import asyncio
import time

import pytest

from course_booking.payments import PaymentGateway
from course_booking.services.enrollment_service import (
    charge_enrollment,
    payment_summary,
)

pytestmark = pytest.mark.stage5

CONCURRENT_CHARGES = 5
MUST_FINISH_WITHIN = 0.9


def test_five_charges_overlap_instead_of_queueing():
    """The trap: an `async def` that blocks is slower than a plain function.

    `async def` does not make anything concurrent. Handing control back does,
    and a call that sleeps without awaiting never hands anything back.
    """
    gateway = PaymentGateway()

    async def five_at_once():
        return await asyncio.gather(
            *(
                charge_enrollment(gateway, "s-%d" % number, 49.0)
                for number in range(CONCURRENT_CHARGES)
            )
        )

    started = time.perf_counter()
    results = asyncio.run(five_at_once())
    elapsed = time.perf_counter() - started

    assert len(results) == CONCURRENT_CHARGES
    assert elapsed < MUST_FINISH_WITHIN, (
        "%d calls of 0.3s took %.1fs: they ran sequentially. Is there a "
        "blocking call inside an async def?" % (CONCURRENT_CHARGES, elapsed)
    )


def test_the_charge_actually_reaches_the_gateway():
    gateway = PaymentGateway()

    result = asyncio.run(charge_enrollment(gateway, "s-1", 49.0))

    assert result.status == "charged"
    assert result.amount == 49.0
    assert len(gateway.charges) == 1, (
        "The gateway was never called. Whatever you replaced the sleep with, "
        "the charge still has to happen."
    )


def test_the_summary_describes_a_payment_and_not_a_coroutine():
    gateway = PaymentGateway()

    summary = asyncio.run(payment_summary(gateway, "s-1", 49.0))

    assert "coroutine" not in summary, (
        "payment_summary answered %r. Calling an async def hands you a "
        "coroutine object, not a result, and the payment never happened. One "
        "missing `await` is all it takes." % summary
    )
    assert "charged" in summary
    assert "49.00" in summary


def test_the_payment_route_answers_with_the_real_status(client):
    response = client.post(
        "/enrollments/payment", params={"student_id": "s-1", "amount": 49.0}
    )

    assert response.status_code == 200, "Got %d: %s" % (
        response.status_code,
        response.text,
    )
    detail = response.json()["detail"]
    assert "coroutine" not in detail, (
        "The API answered %r. A coroutine object went out over HTTP, which "
        "means nobody was charged and the client was told everything is fine."
        % detail
    )
    assert "charged" in detail


def test_the_enrollment_service_is_still_synchronous():
    """The reasoning question from the statement, written as a test.

    EnrollmentService waits for nothing: a dict lookup and a function call both
    return immediately. Making it async would add a keyword to every call site
    and buy exactly nothing.
    """
    from course_booking.services.enrollment_service import EnrollmentService

    assert not asyncio.iscoroutinefunction(EnrollmentService.enroll_student), (
        "enroll_student became a coroutine function. Nothing it calls waits "
        "for anything, so there is nothing for the event loop to do while it "
        "runs: it would be async in name only."
    )
