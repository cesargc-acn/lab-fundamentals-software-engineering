"""Telling a student they are in.

Given, except for the two optional TODOs -- so nothing in this file is needed
to make a test go green. `FakeNotificationSender` is what the tests use: it
records what would have been sent instead of sending it, which is what a fake
is and why this project never reaches for a mocking library.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import List, Protocol

from .domain.models import Course, Student


@dataclass(frozen=True)
class Notification:
    """One message, ready to be delivered."""

    recipient: str
    subject: str
    body: str


class NotificationSender(Protocol):
    """Anything that can tell a student they hold a seat."""

    def notify_enrollment(self, course: Course, student: Student) -> Notification:
        """Send the enrollment message and return what was sent."""
        ...


# TODO [stage-1] 5 (optional): `legacy_booking.enroll_student` builds the email in the
#     middle of the enrollment logic, and `EmailNotificationSender` below repeats the
#     same trick. Give that message a name and a home of its own:
#     - write `build_enrollment_message(course: Course, student: Student) ->
#       Notification` here, moving the string formatting into it;
#     - have `EmailNotificationSender.notify_enrollment` call it instead of formatting
#       anything itself.
#     No test covers this one. You will know it worked if the sender is down to two
#     lines and a `print`.


class EmailNotificationSender:
    """Delivers by email. In the lab it prints the message instead."""

    def notify_enrollment(self, course: Course, student: Student) -> Notification:
        """Send the enrollment message and return what was sent."""
        notification = Notification(
            recipient=student.email,
            subject="You are enrolled in %s" % course.title,
            body=(
                "Hello %s,\n\n"
                "You are now enrolled in %s.\n"
                "Price: %s EUR\n\n"
                "See you in class." % (student.name, course.title, course.price)
            ),
        )
        print("[email] to=%s subject=%s" % (notification.recipient, notification.subject))
        return notification


class FakeNotificationSender:
    """Records instead of sending. Use it in tests and never mock anything else."""

    def __init__(self) -> None:
        self.sent: List[Notification] = []

    def notify_enrollment(self, course: Course, student: Student) -> Notification:
        """Record the enrollment message and return what would have been sent."""
        notification = Notification(
            recipient=student.email,
            subject="You are enrolled in %s" % course.title,
            body="",
        )
        self.sent.append(notification)
        return notification


# TODO [stage-2] 5 (optional): Write a factory `create_notification_sender(channel:
#     str) -> NotificationSender` that returns the sender registered under a channel
#     name: "email" or "fake". Raise `ValueError` for anything else.
#     The caller asks for a channel and gets back something that satisfies
#     `NotificationSender`, never learning which class it got. If you do this one,
#     wire it into `api/dependencies.py` when you reach stage 4.
