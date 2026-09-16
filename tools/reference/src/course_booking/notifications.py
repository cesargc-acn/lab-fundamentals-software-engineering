"""Telling a student they are in.

Given, except for the two optional TODOs. `FakeNotificationSender` is what the
tests use: it records what would have been sent instead of sending it.
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


# @todo stage=1 id=5 kind=optional
# @text `legacy_booking.enroll_student` builds the email in the middle of the
# @text enrollment logic, and `EmailNotificationSender` below repeats the same
# @text trick. Give that message a name and a home of its own: write
# @text `build_enrollment_message(course, student) -> Notification` here, and
# @text have the sender call it instead of formatting strings itself.
# @stub none
# @at 1
def build_enrollment_message(course: Course, student: Student) -> Notification:
    """Build the message a student gets when they enroll on `course`."""
    return Notification(
        recipient=student.email,
        subject="You are enrolled in %s" % course.title,
        body=(
            "Hello %s,\n\n"
            "You are now enrolled in %s.\n"
            "Price: %s EUR\n\n"
            "See you in class." % (student.name, course.title, course.price)
        ),
    )
# @end


class EmailNotificationSender:
    """Delivers by email. In the lab it prints the message instead."""

    def notify_enrollment(self, course: Course, student: Student) -> Notification:
        """Send the enrollment message and return what was sent."""
        # @at 0
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
        # @at 1
        notification = build_enrollment_message(course, student)
        # @end
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


# @todo stage=2 id=5 kind=optional
# @text Write a factory `create_notification_sender(channel)` that returns the
# @text sender for a channel name: "email" or "fake". The caller asks for a
# @text channel and gets back something that satisfies `NotificationSender`; it
# @text never learns which class it got. If you do this one, wire it into
# @text `api/dependencies.py` when you reach stage 4.
# @stub none
# @at 2
def create_notification_sender(channel: str) -> NotificationSender:
    """Return the notification sender registered under `channel`."""
    if channel == "email":
        return EmailNotificationSender()
    if channel == "fake":
        return FakeNotificationSender()
    raise ValueError("unknown notification channel: %r" % channel)
# @end
