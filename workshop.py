#!/usr/bin/env python3
"""Single entry point for the Course Booking workshop.

Every command prints the real tool invocation before running it, so you can
always type that command yourself instead of going through this script.

    python workshop.py setup        install and check the four dependencies
    python workshop.py test 2       run the tests of one stage
    python workshop.py test         run every test (green only at the very end)
    python workshop.py run          start the API with uvicorn
    python workshop.py hint 3       text hints for the TODOs of one stage

Author-only command, not documented in the student README:

    python workshop.py verify-all   rebuild the snapshots, diff them against the
                                    ones committed, and run the cumulative test
                                    suite of every stage against its snapshot.

No third-party imports here on purpose: this file has to run on a machine where
nothing is installed yet.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SRC = ROOT / "src"
TESTS = ROOT / "tests"
SOLUTIONS = ROOT / "solutions"
REQUIREMENTS = ROOT / "requirements.txt"

MIN_PYTHON = (3, 10)
STAGES = (0, 1, 2, 3, 4, 5)
LAST_STAGE = 5
REQUIRED_IMPORTS = ("fastapi", "pydantic", "pytest", "httpx")

HINTS = {
    1: [
        ("1", "core", "EnrollmentPolicy",
         "A Protocol is a normal class that inherits from typing.Protocol. It "
         "declares the method name, its parameters and its return type, and "
         "leaves the body as `...`. No policy has to inherit from it."),
        ("2", "core", "FreeEnrollmentPolicy",
         "A free course has no gate. Read what the legacy function does when "
         "course_type is 'free' and say the same thing in one line. Return a "
         "real bool: the test compares with `is True`."),
        ("3", "core", "LimitedCapacityPolicy",
         "Compare how many students are already enrolled with the number of "
         "seats. The Course object carries both numbers already. Check the "
         "boundary case: 2 of 2 seats taken means full."),
        ("4", "core", "PaidEnrollmentPolicy",
         "A paid course asks two questions, not one: is there a seat left, and "
         "does the student have a payment method? Both have to be true, so "
         "the answer is one expression with `and` in it."),
        ("5", "optional", "notification message",
         "Give the message a name and a home: a function that takes a course "
         "and a student and returns the text. No formatting inside the "
         "enrollment logic."),
    ],
    2: [
        ("1", "core", "CourseRepository",
         "Three methods, no bodies. Write down what the service needs to ask "
         "for, not how a database would answer it."),
        ("2", "core", "EnrollmentRepository",
         "Two methods. exists_for answers a yes/no question, so it returns a "
         "bool, not an object."),
        ("3", "core", "the in-memory repositories",
         "A dict keyed by id is enough. Decide what save does when the id is "
         "already stored, and be consistent between both repositories. If a "
         "test complains that something changed without a save, you handed "
         "back the stored object instead of a copy."),
        ("4", "core", "EnrollmentService",
         "The constructor stores what it is handed and nothing else: no "
         "instantiation, no import of a concrete class. enroll_student then "
         "reads like the steps on a whiteboard. Remember that taking a seat "
         "is two steps, not one: change the count, then save the course."),
        ("5", "optional", "create_notification_sender",
         "One function, one branch, returns a NotificationSender. The caller "
         "never learns which implementation it got."),
    ],
    3: [
        ("1", "core", "the domain errors",
         "Each error carries the data a caller needs to explain itself. The "
         "base class exists so one `except DomainError` can catch the family."),
        ("2", "core", "raise instead of return None",
         "Every `return None` in your service hides a different reason. Give "
         "each reason its own exception and the caller stops guessing. Log the "
         "failure with operation and error_type before raising, because "
         "nothing after a raise ever runs."),
        ("3", "core", "the Pydantic schemas",
         "A request model describes what may come in; a response model "
         "describes what goes out. They are not the same model and they do not "
         "have to share fields."),
        ("4", "optional", "field validator",
         "Pydantic can run your own check after the type check. Reject a value "
         "by raising ValueError with a message a human can read."),
    ],
    4: [
        ("1", "core", "the course routes",
         "The router owns the HTTP vocabulary: path, status code, response "
         "model. Everything else belongs to the service."),
        ("2", "core", "POST /enrollments",
         "201 is not the default status code. Say it in the decorator rather "
         "than building a Response by hand. The route catches nothing: three "
         "handlers in main.py do that for every router at once."),
        ("3", "core", "dependencies.py",
         "A dependency is a function that returns the thing. Depends calls it "
         "for you, and the route never builds a repository itself. Write "
         "these before the routes, or the routes have nothing to ask for."),
        ("4", "core", "the exception handlers",
         "One handler turns one domain error into one HTTP status. Register "
         "them on the app so every router gets the same mapping for free."),
        ("5", "optional", "pagination",
         "limit and offset are query parameters with defaults. Slice the list "
         "the repository returns."),
    ],
    5: [
        ("1", "core", "the blocking call",
         "Read the function the way the event loop reads it: which line stops "
         "every other request while it waits? There is an awaitable version of "
         "that call. The delay is meant to stay; it is meant to stop "
         "blocking."),
        ("2", "core", "the forgotten await",
         "Calling an async def hands you a coroutine, not a result. The proof "
         "shows up in the response body: start the server and call the payment "
         "route before you fix it."),
        ("3", "optional", "asyncio.gather",
         "Three independent calls do not need to take turns. Awaiting in a "
         "loop is right only when the next call needs the last answer."),
    ],
}


# --------------------------------------------------------------------------
# plumbing
# --------------------------------------------------------------------------

def announce(command):
    """Print the real command before running it."""
    print("→ " + command)
    print()
    # The subprocess writes straight to the terminal, so this has to be out of
    # the buffer before it starts, or the two come out interleaved backwards.
    sys.stdout.flush()


def run(command_line, argv, cwd=None, env=None):
    """Print `command_line`, then execute `argv`. Returns the exit code."""
    announce(command_line)
    return subprocess.call(argv, cwd=str(cwd) if cwd else None, env=env)


def pytest_argv(marker_expression=None, verbose=True):
    argv = [sys.executable, "-m", "pytest"]
    printed = ["pytest"]
    if marker_expression:
        argv += ["-m", marker_expression]
        printed += ["-m", marker_expression]
    if verbose:
        argv.append("-v")
        printed.append("-v")
    return argv, " ".join(printed)


def env_with_src(src_dir):
    env = dict(os.environ)
    existing = env.get("PYTHONPATH", "")
    env["PYTHONPATH"] = str(src_dir) + (os.pathsep + existing if existing else "")
    return env


# --------------------------------------------------------------------------
# setup
# --------------------------------------------------------------------------

def command_setup(_args):
    current = sys.version_info
    if current < MIN_PYTHON:
        print("FAIL: this workshop needs Python %d.%d or newer, and this is "
              "Python %d.%d.%d." % (MIN_PYTHON + current[:3]))
        print("      Interpreter in use: %s" % sys.executable)
        print("      Install a newer Python, or create the virtual environment "
              "with it:")
        print("      python3.12 -m venv .venv")
        return 1

    if not REQUIREMENTS.exists():
        print("FAIL: requirements.txt is missing. Are you in the repository "
              "root? Current directory: %s" % Path.cwd())
        return 1

    code = run(
        "pip install -r requirements.txt",
        [sys.executable, "-m", "pip", "install", "-r", str(REQUIREMENTS)],
    )
    if code != 0:
        print()
        print("FAIL: pip could not install the dependencies (exit code %d)." % code)
        print("      If you are behind a corporate proxy, try:")
        print("      pip install -r requirements.txt "
              "--index-url https://pypi.org/simple")
        return code

    missing = []
    for name in REQUIRED_IMPORTS:
        probe = subprocess.call(
            [sys.executable, "-c", "import %s" % name],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        if probe != 0:
            missing.append(name)

    print()
    if missing:
        print("FAIL: installed, but these imports do not work: %s."
              % ", ".join(missing))
        print("      Run this and read the error it prints:")
        print("      %s -c \"import %s\"" % (sys.executable, missing[0]))
        return 1

    print("PASS: Python %d.%d.%d, and fastapi, pydantic, pytest and httpx all "
          "import." % current[:3])
    print()
    print("Next: python workshop.py test 0   (it should be green already)")
    return 0


# --------------------------------------------------------------------------
# test / run / hint
# --------------------------------------------------------------------------

def command_test(args):
    if args.stage is None:
        argv, printed = pytest_argv()
        print("Running the whole suite. It is only fully green once you have "
              "finished stage 5.")
        print()
        return run(printed, argv, cwd=ROOT)

    if args.stage not in STAGES:
        print("FAIL: there is no stage %s. Pick one of: %s."
              % (args.stage, ", ".join(str(s) for s in STAGES)))
        return 1

    argv, printed = pytest_argv("stage%d" % args.stage)
    code = run(printed, argv, cwd=ROOT)
    if code != 0 and args.stage > 0:
        print()
        print("Red is the normal state of a stage you have not finished yet.")
        print("Read the first failure from the top: the test name says what "
              "was expected,")
        print("and the message under AssertionError says what went wrong.")
        print()
        for command, purpose in (
            ('grep -rn "TODO \\[stage-%d\\]" src/' % args.stage,
             "what is still unwritten"),
            ("python workshop.py hint %d" % args.stage, "nudges, no code"),
            ("stages/%02d-*.md" % args.stage, "the full statement"),
        ):
            print("  %-34s %s" % (command, purpose))
    return code


def command_run(_args):
    print("The API will be served on http://127.0.0.1:8000")
    print("The interactive documentation is on http://127.0.0.1:8000/docs")
    print("Stop it with Ctrl+C.")
    print()
    return run(
        "uvicorn course_booking.main:app --reload",
        [sys.executable, "-m", "uvicorn", "course_booking.main:app", "--reload"],
        cwd=ROOT,
        env=env_with_src(SRC),
    )


def command_hint(args):
    if args.stage not in HINTS:
        print("FAIL: there are no hints for stage %s. Stages with hints: %s."
              % (args.stage, ", ".join(str(s) for s in sorted(HINTS))))
        return 1

    print("Hints for stage %d. They point at the idea, never at the code." % args.stage)
    print()
    for number, kind, title, text in HINTS[args.stage]:
        print("TODO [stage-%d] %s (%s) - %s" % (args.stage, number, kind, title))
        for line in wrap(text, 72):
            print("    " + line)
        print()
    print("The full statement is in stages/%02d-*.md, and every term it uses "
          "is defined in GLOSSARY.md." % args.stage)
    return 0


def wrap(text, width):
    words = text.split()
    lines = []
    current = ""
    for word in words:
        candidate = (current + " " + word).strip()
        if len(candidate) > width and current:
            lines.append(current)
            current = word
        else:
            current = candidate
    if current:
        lines.append(current)
    return lines


# --------------------------------------------------------------------------
# helpers
# --------------------------------------------------------------------------

def build_workspace(workspace, src_dir):
    """Copy pyproject + tests + a given src/ into `workspace`, return its src."""
    shutil.copyfile(ROOT / "pyproject.toml", workspace / "pyproject.toml")
    shutil.copytree(TESTS, workspace / "tests")
    target = workspace / "src"
    shutil.copytree(src_dir, target)
    return target


# --------------------------------------------------------------------------
# verify-all (author only)
# --------------------------------------------------------------------------

def command_verify_all(_args):
    sys.path.insert(0, str(ROOT / "tools"))
    try:
        import build_snapshots
    except ImportError:
        print("FAIL: tools/build_snapshots.py is missing.")
        return 1

    failures = []

    print("1. The committed src/ and solutions/ match the reference template")
    print()
    drift = build_snapshots.check_up_to_date()
    if drift:
        for line in drift:
            print("   FAIL: %s" % line)
        failures.append("snapshots are stale, run: python tools/build_snapshots.py")
    else:
        print("   PASS: every generated file is up to date")
    print()

    print("2. Chaining: stage N snapshot only has the TODOs of stages after N")
    print()
    for stage in range(1, LAST_STAGE + 1):
        problems = build_snapshots.check_todo_visibility(
            SOLUTIONS / ("stage-%02d" % stage) / "src", stage
        )
        if problems:
            for line in problems:
                print("   FAIL: stage-%02d: %s" % (stage, line))
            failures.append("stage-%02d has the wrong TODOs" % stage)
        else:
            print("   PASS: stage-%02d" % stage)
    problems = build_snapshots.check_todo_visibility(SRC, 0)
    if problems:
        for line in problems:
            print("   FAIL: src/: %s" % line)
        failures.append("src/ has the wrong TODOs")
    else:
        print("   PASS: src/ (every TODO of stages 1 to %d)" % LAST_STAGE)
    print()

    print("3. Each snapshot passes the tests of its stage and of every stage "
          "before it")
    print()
    for stage in range(1, LAST_STAGE + 1):
        marker = " or ".join("stage%d" % n for n in range(0, stage + 1))
        snapshot_src = SOLUTIONS / ("stage-%02d" % stage) / "src"
        code = run_suite(snapshot_src, marker)
        label = "stage-%02d against '%s'" % (stage, marker)
        if code == 0:
            print("   PASS: %s" % label)
        else:
            print("   FAIL: %s" % label)
            failures.append(label)

    code = run_suite(SRC, "stage0")
    if code == 0:
        print("   PASS: src/ against 'stage0' (green on a fresh clone)")
    else:
        print("   FAIL: src/ against 'stage0' (it has to be green on a fresh clone)")
        failures.append("src/ stage0")

    code = run_suite(SRC, "stage1")
    if code != 0:
        print("   PASS: src/ against 'stage1' fails, as it must before any work")
    else:
        print("   FAIL: src/ passes stage1 without the student writing anything")
        failures.append("src/ stage1 is already green")
    print()

    print("4. The canonical vocabulary is spelled the same everywhere")
    print()
    try:
        import check_vocabulary
    except ImportError:
        print("   FAIL: tools/check_vocabulary.py is missing")
        failures.append("check_vocabulary.py is missing")
    else:
        problems = check_vocabulary.check()
        if problems:
            for line in problems[:20]:
                print("   FAIL: %s" % line)
            failures.append("%d vocabulary problems" % len(problems))
        else:
            print("   PASS: %d identifiers" % len(check_vocabulary.CANONICAL))
    print()

    if failures:
        print("verify-all: FAIL (%d)" % len(failures))
        for line in failures:
            print("  - %s" % line)
        return 1
    print("verify-all: PASS")
    return 0


def run_suite(src_dir, marker_expression):
    with tempfile.TemporaryDirectory() as workspace:
        build_workspace(Path(workspace), src_dir)
        return subprocess.call(
            [sys.executable, "-m", "pytest", "-m", marker_expression, "-q",
             "-p", "no:cacheprovider"],
            cwd=workspace,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )


# --------------------------------------------------------------------------

def build_parser():
    parser = argparse.ArgumentParser(
        prog="python workshop.py",
        description="Course Booking workshop - single entry point.",
    )
    subparsers = parser.add_subparsers(dest="command")

    setup = subparsers.add_parser("setup", help="install and check the dependencies")
    setup.set_defaults(handler=command_setup)

    test = subparsers.add_parser("test", help="run the tests of one stage, or all of them")
    test.add_argument("stage", nargs="?", type=int, help="0 to 5")
    test.set_defaults(handler=command_test)

    serve = subparsers.add_parser("run", help="start the API with uvicorn")
    serve.set_defaults(handler=command_run)

    hint = subparsers.add_parser("hint", help="text hints for the TODOs of one stage")
    hint.add_argument("stage", type=int, help="1 to 5")
    hint.set_defaults(handler=command_hint)

    verify = subparsers.add_parser("verify-all", help=argparse.SUPPRESS)
    verify.set_defaults(handler=command_verify_all)

    return parser


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)
    if not getattr(args, "handler", None):
        parser.print_help()
        return 0
    return args.handler(args)


if __name__ == "__main__":
    sys.exit(main())
