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


class EmailNotificationSender:
    """Delivers by email. In the lab it prints the message instead."""

    def notify_enrollment(self, course: Course, student: Student) -> Notification:
        """Send the enrollment message and return what was sent."""
        notification = build_enrollment_message(course, student)
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


def create_notification_sender(channel: str) -> NotificationSender:
    """Return the notification sender registered under `channel`."""
    if channel == "email":
        return EmailNotificationSender()
    if channel == "fake":
        return FakeNotificationSender()
    raise ValueError("unknown notification channel: %r" % channel)
