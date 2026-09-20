# Course Booking API — hands-on lab

You are handed a working enrollment system that nobody wants to touch: one
function, ninety lines, validation and business rules and email formatting all
in the same place.

Over five stages you will rebuild it into a FastAPI application with a domain layer,
injected dependencies, named errors and one honest use of async — without ever
breaking the tests that pin down what the old code does.

## Before you start

**You need to be comfortable with:** writing Python functions and classes,
running a command in a terminal, and reading a stack trace.

**You need installed:** Git and Python 3.10 or newer. On Windows, start at
[Git on Windows](#git-on-windows) and [Python on Windows](#python-on-windows) —
between them they cover installing both from scratch and updating a version you
already have.

**You do not need to know:** FastAPI, Pydantic, `typing.Protocol`, dependency
injection, the repository pattern, or `asyncio`. Each stage teaches the piece
it needs, and every term the statements use is defined in
[GLOSSARY.md](GLOSSARY.md) — keep that page open in a second tab.

Nothing you write here is thrown away. Each stage starts from the code the
previous one left behind, so **do the stages in order**: stage 3 tests call the
service you write in stage 2.

## What is in the repository

```
workshop.py                     the only command you run. setup, test, run, hint
README.md                       this page
GLOSSARY.md                     every term the statements use, defined
stages/                         the five statements. Read one before you code
tests/                          the tests. You never edit these
solutions/                      the project at the end of each stage, plus notes
src/course_booking/             your code. Every TODO lives here
├── legacy_booking.py           the code you start from. Leave it alone
├── payments.py                 a slow external call, for stage 5
├── notifications.py            sending, and a fake for tests
├── domain/
│   ├── models.py               Course, Student, Enrollment, Instructor
│   ├── policies.py             stage 1
│   └── errors.py               stage 3
├── repositories.py             stage 2
├── services/enrollment_service.py   stages 2, 3 and 5
├── schemas.py                  stage 3
├── api/
│   ├── dependencies.py         stage 4
│   └── routers/                stage 4
└── main.py                     stage 4
```

## Git on Windows

Git is how you get the code, and how you keep your own work in commits while
you move through the stages. Any Git 2.x does everything this lab needs.

Open **PowerShell** (Start menu, type `powershell`) and check first:

```
git --version
```

`git version 2.something` means you are done here — go to
[Python on Windows](#python-on-windows). Anything else (`'git' is not
recognized`) means it is not installed.

### Install Git

Two ways. Either works, pick one.

**A — the installer from git-scm.com.** Use this one if you are unsure.

1. Open <https://git-scm.com/install/windows>.
2. Download **Git for Windows/x64 Setup**. Choose ARM64 only if your machine is
   an ARM device such as a Surface Pro X or a Copilot+ PC.
3. Run it. The installer asks a long list of questions and **the defaults are
   right for this lab**, so Next through them — except for these three, which
   are worth reading:
   - *Choosing the default editor used by Git*: the default is Vim, which is
     hard to leave if you have never used it. Pick **Notepad** or **Visual
     Studio Code** instead.
   - *Adjusting your PATH environment*: keep the recommended option, **"Git
     from the command line and also from 3rd-party software"**. That is what
     makes `git` work in PowerShell and not only in Git Bash.
   - Leave **Git Credential Manager** enabled. It is what signs you in when you
     clone or push.

**B — winget, from a terminal.**

```
winget install --id Git.Git -e --source winget
```

**Check it worked**, in a *new* PowerShell window (the old one does not see the
updated `PATH`):

```
git --version
```

The installer also gives you a terminal called **Git Bash**. The commands in
this README assume PowerShell, so stay in PowerShell unless you know why you
want Git Bash.

### Tell Git who you are

Once per machine, before your first commit. Git refuses to commit without it:

```
git config --global user.name "Your Name"
git config --global user.email "you@example.com"
```

Use the same email as your account on the server you clone from, so your
commits are attributed to you. `git config --global --list` shows what is set.

### Updating a Git you already have

Unlike Python, Git does not install side by side: a new version replaces the
old one and keeps your configuration, so there is nothing to clean up
afterwards. For this lab you do not need the newest version — do this only if
your Git is genuinely old or something is misbehaving.

```
git update-git-for-windows          # from Git 2.17.1 onwards, downloads and runs the installer
winget upgrade --id Git.Git -e      # if you installed it with winget
```

Either can be replaced by downloading the current installer and running it over
the top of the old one. Your `.gitconfig` and your repositories are untouched.

### Git problems worth knowing about

| What you see | What to do |
|---|---|
| `'git' is not recognized as an internal or external command` | open a *new* terminal first. If it persists, re-run the installer and pick **"Git from the command line and also from 3rd-party software"** on the PATH screen. |
| a full-screen editor you cannot get out of | that is Vim. Press `Esc`, then type `:q!` and Enter. Then set a friendlier one: `git config --global core.editor notepad`. |
| `Filename too long` while cloning | `git config --global core.longpaths true`, then clone again. |
| the clone asks for a username and password and rejects them | servers like GitHub no longer accept account passwords. Let Git Credential Manager open the browser window and sign in there. |
| the clone works but files keep locking, or `.venv` behaves strangely | you cloned inside a OneDrive-synced folder. Clone into a plain local path such as `C:\dev\` instead. |

## Python on Windows

This lab needs **Python 3.10 or newer**, and the version to install is
**Python 3.13**: it is the newest line that still ships Windows installers and
it is what the dependencies pinned in `requirements.txt` were built against.

| Version | Use it here? |
|---|---|
| **3.13** | **yes, install this one** |
| 3.11, 3.12 | they work. python.org no longer publishes new installers for them, so there is no reason to pick one on purpose |
| 3.10 | works, but it reaches end of life in October 2026 |
| 3.14 or newer | avoid. The pinned `fastapi==0.115.6` predates it and warns about Pydantic v1 on 3.14; that fix only landed in FastAPI 0.119 |
| 3.9 or older | no. `python workshop.py setup` stops with `this workshop needs Python 3.10 or newer` |

Do not install Python through Anaconda or Miniconda for this lab. The four
dependencies come from `pip` and `requirements.txt`, and a conda environment on
top of that only adds a second package manager to debug.

### What do I already have?

Open **PowerShell** (Start menu, type `powershell`) and run:

```
py --list
```

`py` is the Python launcher that every python.org installer puts on the
machine, and it knows about every Python installed on it. The answer looks
something like:

```
 -V:3.13 *        Python 3.13 (64-bit)
 -V:3.9           Python 3.9 (64-bit)
```

| What you see | What it means |
|---|---|
| a line with 3.13, 3.12, 3.11 or 3.10 | nothing to install — go to [Setup](#setup) and use `py -3.13` (or your version) where it says `python` |
| only older versions, such as 3.9 | install 3.13 next to it: [Install Python 3.13](#install-python-313), then [Upgrading a Python you already have](#upgrading-a-python-you-already-have) |
| `py` is not recognised, or the list is empty | you have no usable Python: [Install Python 3.13](#install-python-313) |
| the Microsoft Store opens | that is a Windows placeholder, not Python: [Install Python 3.13](#install-python-313) |

### Install Python 3.13

Two ways. Either works, pick one.

**A — the installer from python.org.** Use this one if you are unsure.

1. Open <https://www.python.org/downloads/windows/>.
2. Under the latest **Python 3.13.x** release, download **Windows installer
   (64-bit)**: a file named `python-3.13.x-amd64.exe`. Choose ARM64 only if
   your machine is an ARM device such as a Surface Pro X or a Copilot+ PC.
3. Run it and **tick "Add python.exe to PATH"** at the bottom of the first
   screen, before clicking anything else. This is the step people skip and
   then lose twenty minutes to.
4. Click **Install Now**. It installs for your user only, so you do not need
   administrator rights.
5. If the last screen offers **"Disable path length limit"**, click it.

**B — winget, from a terminal.**

```
winget install --exact --id Python.Python.3.13
```

Then close that terminal and open a new one, or the updated `PATH` will not be
visible in it.

**Check it worked**, in a *new* PowerShell window:

```
py -3.13 --version
```

It has to print `Python 3.13.something`. When it does, go to [Setup](#setup).

### Upgrading a Python you already have

Installing 3.13 does not remove the Python already on your machine, and that is
the intended behaviour: Windows keeps versions side by side, and other tools
you use may depend on the old one. There is no in-place "upgrade" from, say,
3.9 to 3.13 — you install 3.13 and then choose it explicitly.

1. Install 3.13 with either method above. Nothing has to be uninstalled first.
2. Use `py -3.13` instead of `python` when you create the virtual environment.
   The launcher runs the version you name regardless of what `PATH` says:

   ```
   py -3.13 -m venv .venv
   ```

   Once `.venv` is active, plain `python` inside it is already the right one.
3. Uninstalling the old version is optional. If you want to: **Settings → Apps
   → Installed apps**, find `Python 3.x.y`, then **…** → Uninstall. Leave
   `Python Launcher` installed.

Two cases behave differently from the above:

- **Same line, newer patch** (3.13.2 → 3.13.15): the installer replaces it in
  place, there is nothing to choose.
- **Installed with winget**: `winget upgrade Python.Python.3.13` keeps that
  line up to date, but it will never move you from 3.9 to 3.13. Those are
  different packages; install `Python.Python.3.13` as above.

**If you already built `.venv` with the old interpreter, delete it and build it
again.** A virtual environment is tied to the Python that created it and
installing a newer Python does not change it:

```
rmdir /s /q .venv
py -3.13 -m venv .venv
```

### Windows problems worth knowing about

| What you see | What to do |
|---|---|
| typing `python` opens the Microsoft Store | that is a Windows placeholder alias. **Settings → Apps → Advanced app settings → App execution aliases**, turn **off** `python.exe` and `python3.exe`. Or simply use `py`. |
| `'python' is not recognized as an internal or external command` | the PATH checkbox was not ticked. Use `py` instead, or re-run the installer, choose **Modify**, and tick **"Add Python to environment variables"** under Advanced Options. |
| `Activate.ps1 cannot be loaded because running scripts is disabled on this system` | PowerShell blocks scripts by default. Run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass` in that window and activate again. It affects that window only. |
| `py --list` shows 3.13 but `python --version` says 3.9 | both are installed and the old one comes first on `PATH`. Use `py -3.13` to build the venv and ignore bare `python` until it is active. |

## Setup

1. Get the code. On Windows, run this from PowerShell in a plain local
   folder such as `C:\dev` — not inside a OneDrive-synced one:

   ```
   git clone <REPOSITORY-URL>
   cd lab-fundamentals-software-engineering
   ```

2. Create a virtual environment with Python 3.10 or newer, and activate it.
   On Windows use `py -3.13`, which picks that interpreter whatever your
   `PATH` says — see [Python on Windows](#python-on-windows) if you do not
   have it yet:

   ```
   py -3.13 -m venv .venv           # Windows
   .venv\Scripts\activate

   python3 -m venv .venv            # macOS and Linux
   source .venv/bin/activate
   ```

   You will know it worked because your prompt now starts with `(.venv)`.
   If you open a new terminal later, activate it again.

3. Install and check everything, from the repository root:

   ```
   python workshop.py setup
   ```

   It installs the four dependencies and checks them. It prints `PASS`, or it
   prints the one thing that is wrong and the command that fixes it.

4. Confirm the starting point is green:

   ```
   python workshop.py test 0
   ```

   Those tests pass before you write anything. If they do not, stop and fix the
   setup — everything after this assumes they are green.

### When setup goes wrong

| What you see | What it means | What to do |
|---|---|---|
| `No module named fastapi` | the virtual environment is not active, or `setup` was never run | activate `.venv`, then `python workshop.py setup` |
| `No module named course_booking` | you are not in the repository root | `cd` to the folder that contains `workshop.py` |
| `python: command not found` | your system spells it differently | `py` on Windows, `python3` on macOS and Linux |
| `this workshop needs Python 3.10 or newer` | the venv was built with an old interpreter | delete `.venv` and build it again: `rmdir /s /q .venv` then `py -3.13 -m venv .venv` on Windows (see [Upgrading a Python you already have](#upgrading-a-python-you-already-have)), `rm -rf .venv` then `python3.13 -m venv .venv` elsewhere |
| `Activate.ps1 cannot be loaded because running scripts is disabled` | PowerShell blocks scripts by default | `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again |
| pip cannot reach the index | corporate proxy | `pip install -r requirements.txt --index-url https://pypi.org/simple` |

## How to work

Five stages. Read the statement first, then open the file, then write code,
then run the tests. Repeat until green.

| Stage | Statement | Run its tests |
|---|---|---|
| 1 · Domain and enrollment policy | [stages/01-domain-and-policy.md](stages/01-domain-and-policy.md) | `python workshop.py test 1` |
| 2 · Repository and dependency injection | [stages/02-repository-and-injection.md](stages/02-repository-and-injection.md) | `python workshop.py test 2` |
| 3 · Domain errors and validation | [stages/03-errors-and-validation.md](stages/03-errors-and-validation.md) | `python workshop.py test 3` |
| 4 · FastAPI: routes, Depends and HTTP codes | [stages/04-fastapi-routes-and-errors.md](stages/04-fastapi-routes-and-errors.md) | `python workshop.py test 4` |
| 5 · Async: when and why | [stages/05-async-when-and-why.md](stages/05-async-when-and-why.md) | `python workshop.py test 5` |

### Finding the work

Every place you have to write something is marked with a comment that names its
stage and its number, and the number matches the statement:

```
# TODO [stage-2] 3 (core): Keep the courses somewhere. A dict keyed by course
#     id is enough, and it makes `get_by_id` a one-liner.
```

`core` tasks are covered by tests and are what "done" means.
`optional` tasks have no test; do them if you have time, skip them without
guilt if you do not.

To see everything a stage still expects from you:

```
grep -rn "TODO \[stage-2\]" src/               # macOS, Linux
findstr /s /n /c:"TODO [stage-2]" src\*.py     # Windows
```

Until you fill one in, the code raises `NotImplementedError("TODO [stage-2] 3")`
— so a failing test that says exactly that is telling you which TODO is next,
not that something is broken.

### Reading a test failure

The tests are the contract, and their failure messages are written to be read.
A run looks like this:

```
FAILED tests/test_stage1_policies.py::test_a_free_course_always_says_yes[2]
E   AssertionError: FreeEnrollmentPolicy refused a student on a free course
E   with 2 enrolled. The legacy code does not count seats on free courses,
E   and neither should this policy.
```

Three things to take from it: the file, the test name (it says what was
expected in words), and the message under `AssertionError` (it says what went
wrong and usually what to do). The `[2]` at the end is the input that failed —
the same test ran over several values and this is the one that broke.

Useful variations, all of which the workshop script prints for you before it
runs them, so you can type them yourself:

```
pytest -m stage1                                 every test of stage 1
pytest -m stage1 -k free                         only the ones with "free" in the name
pytest -m stage1 -x                              stop at the first failure
pytest tests/test_stage1_policies.py -q          one file, quiet output
```

### A stage is done when its tests are green

Not when your code looks like the reference. There are several correct ways to
solve most of these tasks, and the tests are deliberately written so that they
never inspect *how* you did it.

Stage 0 deserves a special mention: `python workshop.py test 0` is green before
you write anything, and it must stay green to the very end. Those tests
describe what the legacy code does, and everything you build has to keep
agreeing with them. That is the whole idea of refactoring under a safety net.

### Other commands

```
python workshop.py hint 3     text hints for one stage. Ideas, never code
python workshop.py run        start the API, then open http://127.0.0.1:8000/docs
python workshop.py test       the whole suite. Only fully green at the very end
```

Every command prints the real tool invocation before running it, so you can
always type that command yourself instead.

## When you get stuck

In this order, and there is no shame in reaching step 4:

1. **Re-read the failing test.** It names the behaviour it wants in its own
   name and explains the failure in its message.
2. **Run `python workshop.py hint <stage>`.** Short nudges towards the idea,
   with no code in them.
3. **Read the theory reference** at the bottom of the stage statement.
4. **Open `solutions/stage-0N/`.** Compare it with your own file, or take it
   as the starting point for the next stage and keep moving. Both are normal
   uses — see [Solutions](#solutions).

## Solutions

`solutions/` holds five directories, one per stage. Each one is **the whole
project as it looks at the end of that stage**, not only the files you touched
in it. `solutions/stage-03/` is every file of `src/`, with stages 1, 2 and 3
written and stages 4 and 5 still marked TODO — exactly how your own `src/`
should look the minute `python workshop.py test 3` goes green.

That is why there are five and not one finished version. One finished version
answers *what does the end look like*. This lab has to answer a different
question five times: *what should I have by now, and what should still be
missing?*

They are one way to solve each stage, never the only one, and they are there
for three different moments.

### To compare, once a stage is green

Open the matching directory next to your own file and read the differences.
Most of these tasks have several correct answers and yours may well be one of
them, so a difference is something to think about, not a mistake to go and fix.

### To read, when you are stuck

Retyping a solution you then understand beats staring at a blank file for forty
minutes. This is step 4 of [When you get stuck](#when-you-get-stuck) and it is
a normal step, not a failure.

### To catch up, when a stage will not come out

Because each directory is a complete project, you can take one as your new
starting point and go on with the next stage instead of staying blocked. That
is the reason the stages after it are still marked TODO in there.

`python workshop.py test 2` is green again, the TODOs of stages 3, 4 and 5 are
waiting in the files, and you can open the stage 3 statement and keep going.

### Every directory also has a NOTES.md

And it is usually worth more than the code beside it. It explains the
decisions the code cannot explain on its own — why a `Protocol` and not an
abstract base class, why one comparison is duplicated on purpose — and it
ends with a list of the other answers that are equally correct. Read that
last part even when your own version is already green.

## Pace

The times on each statement are a rough guide for somebody who has seen the
ideas before. Taking twice as long the first time is normal and is not a
signal about you.

There is no mark and nothing to hand in. Reaching stage 3 having understood it
is worth more than reaching stage 5 by copying, and if a stage is not clicking,
taking its solution as your starting point and moving on is a legitimate way to
spend the time. [Solutions](#solutions) shows how.
