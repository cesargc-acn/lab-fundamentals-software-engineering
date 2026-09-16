"""HTTP for enrollments.

The enrollment route is three lines long, and that is the measure of whether
stage 2 went well: everything it would have contained lives in the service.
"""

from __future__ import annotations

from typing import Dict

from fastapi import APIRouter, Depends

from ...domain.models import Student
from ...payments import PaymentGateway
from ...schemas import CreateEnrollmentRequest, EnrollmentResponse
from ...services.enrollment_service import EnrollmentService, payment_summary
from ..dependencies import get_enrollment_service, get_payment_gateway

router = APIRouter(prefix="/enrollments", tags=["enrollments"])


# TODO [stage-4] 2 (core): Finish the route below: turn the request into a `Student`,
#     hand it to the service, and answer 201 with an `EnrollmentResponse`. A created
#     resource is a 201, and 201 is not the default, so say so in the decorator. None
#     of the three domain errors is caught here; `main.py` turns each of them into a
#     status code, once, for every router.
@router.post("")
def create_enrollment(
    payload: CreateEnrollmentRequest,
    service: EnrollmentService = Depends(get_enrollment_service),
) -> EnrollmentResponse:
    """Enroll a student on a course."""
    raise NotImplementedError("TODO [stage-4] 2")


@router.post("/payment")
async def pay_enrollment(
    student_id: str,
    amount: float = 49.0,
    gateway: PaymentGateway = Depends(get_payment_gateway),
) -> Dict[str, str]:
    """Given. Charge a student, and say what happened.

    The only `async def` route in the project, because it is the only one that
    waits for anything. Stage 5 is about the code it calls, not about this
    function.
    """
    return {
        "student_id": student_id,
        "detail": await payment_summary(gateway, student_id, amount),
    }
