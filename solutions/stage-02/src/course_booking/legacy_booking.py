"""The enrollment code the team has today.

It works. Every test in tests/test_stage0_characterization.py passes against it
before you write a single line. That is the point of the first ten minutes: the
problem with this file is not that it is broken.

Leave it exactly as it is. The stages that follow rebuild it next to it, and the
characterization tests stay green the whole time as proof that you understood
what the old code did before you replaced it.
"""

COURSES = {
    "python-basics": {
        "title": "Python Basics",
        "type": "free",
        "capacity": 2,
        "price": 0.0,
        "students": [],
    },
    "testing-101": {
        "title": "Testing 101",
        "type": "limited",
        "capacity": 2,
        "price": 0.0,
        "students": [],
    },
    "architecture-in-practice": {
        "title": "Architecture in Practice",
        "type": "paid",
        "capacity": 3,
        "price": 149.0,
        "students": [],
    },
}

ENROLLMENTS = {}

SENT_EMAILS = []


def enroll_student(course_id, student_id, student_email, has_payment_method=False):
    if course_id is None or course_id == "":
        return None
    if student_id is None or student_id == "":
        return None
    if student_email is None or "@" not in student_email:
        return None
    if course_id not in COURSES:
        return None

    course = COURSES[course_id]
    key = course_id + ":" + student_id
    if key in ENROLLMENTS:
        return False

    if course["type"] == "free":
        allowed = True
    elif course["type"] == "limited":
        if len(course["students"]) < course["capacity"]:
            allowed = True
        else:
            allowed = False
    elif course["type"] == "paid":
        if len(course["students"]) >= course["capacity"]:
            allowed = False
        elif not has_payment_method:
            allowed = False
        else:
            allowed = True
    else:
        allowed = False

    if not allowed:
        return False

    course["students"].append(student_id)
    ENROLLMENTS[key] = {
        "course_id": course_id,
        "student_id": student_id,
        "status": "confirmed",
    }

    subject = "You are enrolled in " + course["title"]
    body = (
        "Hello " + student_id + ",\n\n"
        "You are now enrolled in " + course["title"] + ".\n"
        "Price: " + str(course["price"]) + " EUR\n\n"
        "See you in class."
    )
    SENT_EMAILS.append({"to": student_email, "subject": subject, "body": body})

    return {
        "course_id": course_id,
        "student_id": student_id,
        "status": "confirmed",
        "title": course["title"],
        "price": course["price"],
        "seats_taken": len(course["students"]),
    }
