#!/usr/bin/env python3
"""Author tool. Builds every copy of the source tree from one template.

`tools/reference/src/` holds the finished implementation, annotated with the
stage each piece belongs to. This script renders it at six levels:

    level 0  -> src/                      the student's starting point
    level 1  -> solutions/stage-01/src/   stage 1 done, stages 2-5 still TODO
    ...
    level 5  -> solutions/stage-05/src/   everything done

Rendering every tree from the same template is what makes the chaining
invariant true by construction: the snapshot of stage N *is* the starting point
of stage N+1. `python workshop.py verify-all` checks it has not drifted.

Template syntax, all of it inside comments:

    # @todo stage=1 id=2 kind=core        declares a TODO for this region
    # @text one line of the instruction   (repeatable, follows its @todo)
    # @stub pass                          stub flavour: raise (default)/pass/none
    # @at 0                               code used from level 0 on
    # @at 1                               code used from level 1 on
    # @end                                closes the region

At level L a region emits the highest `@at S` with S <= L, or the stub when
there is none, always preceded by the TODO comments of the stages still to do.
A region with no `@todo` is a silent variant: it switches code without telling
the student anything.
"""

import difflib
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "tools" / "reference" / "src"
STUDENT_SRC = ROOT / "src"
SOLUTIONS = ROOT / "solutions"
LAST_STAGE = 5
COMMENT_WIDTH = 86

DIRECTIVE = re.compile(r"^(\s*)#\s*@(todo|text|stub|at|end)\b\s*(.*)$")


class Todo:
    def __init__(self, stage, number, kind):
        self.stage = stage
        self.number = number
        self.kind = kind
        self.text = []

    @property
    def label(self):
        return "TODO [stage-%d] %s" % (self.stage, self.number)


class Region:
    def __init__(self, indent):
        self.indent = indent
        self.todos = []
        self.stub = "raise"
        self.variants = []          # list of (stage, [lines])

    def render(self, level):
        out = []
        for todo in self.todos:
            if todo.stage > level:
                out.extend(comment_block(self.indent, todo))
        chosen = None
        for stage, lines in self.variants:
            if stage <= level and (chosen is None or stage >= chosen[0]):
                chosen = (stage, lines)
        if chosen is not None:
            out.extend(chosen[1])
        elif self.stub == "raise":
            first = self.todos[0]
            out.append('%sraise NotImplementedError("%s")' % (self.indent, first.label))
        elif self.stub == "pass":
            out.append(self.indent + "pass")
        return out


def comment_block(indent, todo):
    head = "# %s (%s): " % (todo.label, todo.kind)
    words = " ".join(todo.text).split()
    lines = []
    current = indent + head
    prefix = indent + "#     "
    for word in words:
        candidate = current + ("" if current.endswith(" ") else " ") + word
        if len(candidate) > COMMENT_WIDTH and current.strip() not in ("#", head.strip()):
            lines.append(current.rstrip())
            current = prefix + word
        else:
            current = candidate
    lines.append(current.rstrip())
    return lines


def parse(text):
    """Split a template file into plain strings and Region objects."""
    segments = []
    region = None
    current_todo = None
    current_variant = None

    for raw in text.splitlines():
        match = DIRECTIVE.match(raw)
        if not match:
            if region is None:
                segments.append(raw)
            elif current_variant is not None:
                current_variant.append(raw)
            elif raw.strip():
                raise SyntaxError("code inside a region but outside @at: %r" % raw)
            continue

        indent, keyword, rest = match.groups()
        if keyword == "todo":
            if region is None:
                region = Region(indent)
                segments.append(region)
            fields = dict(part.split("=", 1) for part in rest.split())
            current_todo = Todo(int(fields["stage"]), fields["id"], fields["kind"])
            region.todos.append(current_todo)
            current_variant = None
        elif keyword == "text":
            if current_todo is None:
                raise SyntaxError("@text without a preceding @todo")
            current_todo.text.append(rest)
        elif keyword == "stub":
            if region is None:
                raise SyntaxError("@stub outside a region")
            region.stub = rest.strip()
        elif keyword == "at":
            if region is None:
                region = Region(indent)
                segments.append(region)
            current_variant = []
            region.variants.append((int(rest.strip()), current_variant))
        elif keyword == "end":
            if region is None:
                raise SyntaxError("@end without a region")
            region = None
            current_todo = None
            current_variant = None

    if region is not None:
        raise SyntaxError("a region was left open")
    return segments


def render(segments, level):
    lines = []
    for segment in segments:
        if isinstance(segment, Region):
            lines.extend(segment.render(level))
        else:
            lines.append(segment)
    return "\n".join(lines).rstrip("\n") + "\n"


def template_files():
    return sorted(p for p in TEMPLATE.rglob("*.py"))


def render_tree(level):
    """Return {relative path: file content} for one level."""
    tree = {}
    for path in template_files():
        relative = path.relative_to(TEMPLATE)
        try:
            tree[relative] = render(parse(path.read_text()), level)
        except SyntaxError as error:
            raise SyntaxError("%s: %s" % (relative, error))
    return tree


def all_todos():
    todos = []
    for path in template_files():
        for segment in parse(path.read_text()):
            if isinstance(segment, Region):
                todos.extend(segment.todos)
    return todos


def expected_outputs():
    """Every file this tool owns: {absolute path: content}."""
    outputs = {}
    for level in range(0, LAST_STAGE + 1):
        base = STUDENT_SRC if level == 0 else SOLUTIONS / ("stage-%02d" % level) / "src"
        for relative, content in render_tree(level).items():
            outputs[base / relative] = content
    return outputs


def write_all():
    for level in range(0, LAST_STAGE + 1):
        base = STUDENT_SRC if level == 0 else SOLUTIONS / ("stage-%02d" % level) / "src"
        if base.exists():
            shutil.rmtree(base)
    outputs = expected_outputs()
    for path, content in sorted(outputs.items()):
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content)
    return outputs


def check_up_to_date():
    """Return a list of human-readable drift messages. Empty means up to date."""
    problems = []
    outputs = expected_outputs()
    for path, content in sorted(outputs.items()):
        relative = path.relative_to(ROOT)
        if not path.exists():
            problems.append("%s is missing" % relative)
            continue
        on_disk = path.read_text()
        if on_disk != content:
            diff = list(difflib.unified_diff(
                on_disk.splitlines(), content.splitlines(),
                fromfile="committed", tofile="generated", lineterm="", n=1))
            problems.append("%s differs from the template:\n      %s"
                            % (relative, "\n      ".join(diff[:12])))
    owned_roots = [STUDENT_SRC] + [SOLUTIONS / ("stage-%02d" % n) / "src"
                                   for n in range(1, LAST_STAGE + 1)]
    for base in owned_roots:
        for path in base.rglob("*.py"):
            if path not in outputs:
                problems.append("%s is not generated by the template" % path.relative_to(ROOT))
    return problems


def check_todo_visibility(src_dir, level):
    """Check `src_dir` shows exactly the TODOs of the stages after `level`."""
    problems = []
    expected = set()
    for todo in all_todos():
        if todo.stage > level:
            expected.add(todo.label)
    found = set()
    pattern = re.compile(r"TODO \[stage-(\d)\] (\S+)")
    for path in sorted(Path(src_dir).rglob("*.py")):
        for stage, number in pattern.findall(path.read_text()):
            label = "TODO [stage-%s] %s" % (stage, number)
            found.add(label)
            if int(stage) <= level:
                problems.append("%s still carries %s, which belongs to a stage "
                                "already done" % (path.relative_to(ROOT), label))
    for label in sorted(expected - found):
        problems.append("%s is nowhere to be found" % label)
    return problems


def main():
    outputs = write_all()
    print("build_snapshots: wrote %d files" % len(outputs))
    for level in range(0, LAST_STAGE + 1):
        base = STUDENT_SRC if level == 0 else SOLUTIONS / ("stage-%02d" % level) / "src"
        problems = check_todo_visibility(base, level)
        status = "OK" if not problems else "PROBLEMS"
        print("  level %d -> %-28s %s" % (level, str(base.relative_to(ROOT)), status))
        for line in problems:
            print("      %s" % line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
