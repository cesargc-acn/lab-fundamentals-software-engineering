"""A stand-in for a real payment provider.

Given. This is the only component in the project that actually waits for
something: `charge` sleeps for a third of a second, the way a call over the
network would. Stage 5 is built around it, because it is the only place where
async buys you anything.
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List

GATEWAY_LATENCY_SECONDS = 0.3


@dataclass(frozen=True)
class PaymentResult:
    """What the provider answers."""

    student_id: str
    amount: float
    status: str

    def __str__(self) -> str:
        return "%s %.2f EUR" % (self.status, self.amount)


class PaymentGateway:
    """Pretends to be a slow HTTP call to a payment provider."""

    def __init__(self, latency_seconds: float = GATEWAY_LATENCY_SECONDS) -> None:
        self.latency_seconds = latency_seconds
        self.charges: List[PaymentResult] = []

    async def charge(self, student_id: str, amount: float) -> PaymentResult:
        """Charge `student_id`. Takes about a third of a second, like the real one."""
        await asyncio.sleep(self.latency_seconds)
        status = "charged" if amount >= 0 else "declined"
        result = PaymentResult(student_id=student_id, amount=amount, status=status)
        self.charges.append(result)
        return result
