#!/usr/bin/env python3
"""Author tool. The names on the slides and the names in the editor must match.

Section 10 of the plan fixes the vocabulary of the workshop. A student who sees
`EnrollmentService` on a slide and `enrollment_service` in the code spends
attention on the difference instead of on the idea, so this script checks three
things across every text file in the repository:

  1. every canonical identifier appears, spelled exactly as agreed;
  2. no canonical class name appears in a different casing;
  3. none of the usual near-misses shows up: the British single-l spelling,
     or a camelCase version of a snake_case method.
"""

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

CLASSES = [
    "EnrollmentService", "CourseRepository", "StudentRepository",
    "EnrollmentRepository", "InMemoryCourseRepository", "EnrollmentPolicy",
    "FreeEnrollmentPolicy", "PaidEnrollmentPolicy", "LimitedCapacityPolicy",
    "NotificationSender", "FakeNotificationSender",
]
ERRORS = [
    "DomainError", "CourseNotFoundError", "EnrollmentNotAllowedError",
    "StudentAlreadyEnrolledError",
]
ENTITIES = [
    "Course", "Student", "Enrollment", "Instructor", "Notification",
    "CreateCourseRequest", "CourseResponse", "CreateEnrollmentRequest",
    "EnrollmentResponse",
]
METHODS = [
    "enroll_student", "get_by_id", "save", "list_available_courses",
    "notify_enrollment",
]
EVENTS = ["EnrollmentCreated"]

CANONICAL = CLASSES + ERRORS + ENTITIES + METHODS + EVENTS

# Casing is only checked on compound names. `Course` and `Notification` are
# also ordinary English words, and `course` and `notification` are exactly what
# a local variable holding one should be called.
CASE_CHECKED = [
    name for name in CLASSES + ERRORS + ENTITIES + EVENTS
    if sum(1 for character in name if character.isupper()) > 1
]

NEAR_MISSES = [
    (r"\benrol(?!l)", "the British single-l spelling of enroll"),
    (r"\benrollStudent\b", "camelCase version of enroll_student"),
    (r"\bgetById\b", "camelCase version of get_by_id"),
    (r"\blistAvailableCourses\b", "camelCase version of list_available_courses"),
    (r"\bnotifyEnrollment\b", "camelCase version of notify_enrollment"),
    (r"\bexistsFor\b", "camelCase version of exists_for"),
]

SKIP_DIRS = {".git", ".venv", "__pycache__", ".pytest_cache", "node_modules"}
SKIP_FILES = {"plan.md"}
TEXT_SUFFIXES = {".py", ".md", ".toml", ".txt", ".cfg", ".ini", ".yml", ".yaml"}


def text_files():
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file() or path.suffix not in TEXT_SUFFIXES:
            continue
        if path.name in SKIP_FILES:
            continue
        if any(part in SKIP_DIRS for part in path.relative_to(ROOT).parts):
            continue
        yield path


def check():
    problems = []
    documents = [(path, path.read_text()) for path in text_files()]

    for name in CANONICAL:
        pattern = re.compile(r"\b%s\b" % re.escape(name))
        if not any(pattern.search(body) for _, body in documents):
            problems.append("%s never appears in the repository" % name)

    for name in CASE_CHECKED:
        pattern = re.compile(r"\b%s\b" % re.escape(name), re.IGNORECASE)
        for path, body in documents:
            for line_number, line in enumerate(body.splitlines(), start=1):
                for found in pattern.findall(line):
                    if found != name:
                        problems.append(
                            "%s:%d spells %s as %r"
                            % (path.relative_to(ROOT), line_number, name, found)
                        )

    for pattern_text, description in NEAR_MISSES:
        pattern = re.compile(pattern_text)
        for path, body in documents:
            for line_number, line in enumerate(body.splitlines(), start=1):
                if pattern.search(line):
                    problems.append(
                        "%s:%d uses %s" % (path.relative_to(ROOT), line_number, description)
                    )

    return problems


def main():
    problems = check()
    if problems:
        print("check_vocabulary: FAIL (%d)" % len(problems))
        for line in problems:
            print("  - %s" % line)
        return 1
    print("check_vocabulary: PASS (%d identifiers, %d files)"
          % (len(CANONICAL), len(list(text_files()))))
    return 0


if __name__ == "__main__":
    sys.exit(main())
