"""Traces a solution under sys.settrace and prints a JSON execution trace.

main.py launches this as a subprocess (so runaway code can be killed by a
timeout) and writes {"code": str, "run": str} to stdin. `code` is the
solution being visualized; `run` is a short driver that calls into it.

Only frames from the solution are recorded. Each step captures the line about
to execute, every frame's locals and a snapshot of every object reachable from
them, so the frontend can draw arrays, hashmaps, linked lists, trees, etc.
"""

import ast
import builtins
import io
import json
import math
import sys
import types
from collections import deque

MAX_STEPS = 1500
MAX_ITEMS = 150
MAX_HEAP = 400
MAX_STR = 300
MAX_FRAMES = 40

SOLUTION = "<solution>"
DRIVER = "<driver>"
SKIP_CODE = {"<module>", "<listcomp>", "<dictcomp>", "<setcomp>", "<genexpr>", "<lambda>"}
ALLOWED_MODULES = {
    "collections", "heapq", "math", "bisect", "functools", "itertools",
    "typing", "string", "re", "random", "operator", "copy",
}
BLOCKED_BUILTINS = {"open", "input", "exit", "quit", "breakpoint", "help"}
HIDDEN_TYPES = (
    types.FunctionType, types.BuiltinFunctionType, types.MethodType,
    types.ModuleType, type,
)


# ---------------------------------------------------------------------------
# Helpers available to every solution (mirrors what LeetCode predefines)
# ---------------------------------------------------------------------------

class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class TreeNode:
    def __init__(self, val=0, left=None, right=None):
        self.val = val
        self.left = left
        self.right = right


def build_list(vals, cycle_at=-1):
    """[1, 2, 3] -> 1 -> 2 -> 3. cycle_at links the tail back to that index."""
    dummy = tail = ListNode()
    nodes = []
    for v in vals:
        tail.next = ListNode(v)
        tail = tail.next
        nodes.append(tail)
    if 0 <= cycle_at < len(nodes):
        tail.next = nodes[cycle_at]
    return dummy.next


def build_tree(vals):
    """Level-order list (LeetCode style, None for gaps) -> TreeNode."""
    if not vals or vals[0] is None:
        return None
    root = TreeNode(vals[0])
    queue = deque([root])
    i = 1
    while queue and i < len(vals):
        node = queue.popleft()
        if i < len(vals) and vals[i] is not None:
            node.left = TreeNode(vals[i])
            queue.append(node.left)
        i += 1
        if i < len(vals) and vals[i] is not None:
            node.right = TreeNode(vals[i])
            queue.append(node.right)
        i += 1
    return root


def find_node(root, val):
    """Find the TreeNode holding `val` (for problems that take node arguments)."""
    stack = [root]
    while stack:
        node = stack.pop()
        if node is None:
            continue
        if node.val == val:
            return node
        stack += [node.left, node.right]
    return None


def to_plain(v, depth=0):
    """Convert results into plain Python values for display/comparison."""
    if depth > 50:
        return "..."
    if isinstance(v, ListNode):
        out, seen = [], set()
        while v is not None and id(v) not in seen and len(out) < 200:
            seen.add(id(v))
            out.append(to_plain(v.val, depth + 1))
            v = v.next
        return out
    if isinstance(v, TreeNode):
        out, queue = [], deque([v])
        while queue:
            node = queue.popleft()
            if node is None:
                out.append(None)
                continue
            out.append(to_plain(node.val, depth + 1))
            queue.append(node.left)
            queue.append(node.right)
        while out and out[-1] is None:
            out.pop()
        return out
    if isinstance(v, (list, tuple)):
        return type(v)(to_plain(x, depth + 1) for x in v) if isinstance(v, list) else tuple(to_plain(x, depth + 1) for x in v)
    return v


HELPERS = {
    "ListNode": ListNode,
    "TreeNode": TreeNode,
    "build_list": build_list,
    "build_tree": build_tree,
    "find_node": find_node,
}


def safe_import(name, globals=None, locals=None, fromlist=(), level=0):
    if name.split(".")[0] not in ALLOWED_MODULES:
        raise ImportError(f"import of '{name}' is not allowed in the visualizer")
    return __import__(name, globals, locals, fromlist, level)


def make_globals():
    safe_builtins = {k: v for k, v in vars(builtins).items() if k not in BLOCKED_BUILTINS}
    safe_builtins["__import__"] = safe_import
    g = {"__builtins__": safe_builtins, "__name__": "__main__"}
    g.update(HELPERS)
    # Common imports LeetCode solutions assume are present
    exec(
        "from typing import List, Optional, Dict, Set, Tuple\n"
        "from collections import deque, defaultdict, Counter, OrderedDict\n"
        "import heapq, math, bisect\n",
        g,
    )
    return g


# ---------------------------------------------------------------------------
# Snapshot encoding
# ---------------------------------------------------------------------------

def sort_items(items):
    try:
        return sorted(items)
    except TypeError:
        return sorted(items, key=repr)


class Encoder:
    """Encodes values as JSON. Mutable objects go into a per-step heap keyed by
    an id that stays stable for the whole run, so the frontend can diff them
    between steps and draw arrows from variables to the objects they hold."""

    def __init__(self):
        self.ids = {}
        self.keep_alive = []  # stops CPython reusing id()s of freed objects
        self.heap = {}
        self.pending = []

    def begin(self):
        self.heap = {}
        self.pending = []

    def value(self, v, depth=0):
        if v is None or isinstance(v, bool):
            return v
        if isinstance(v, int):
            return v if abs(v) < 2 ** 53 else {"t": "num", "v": str(v)}
        if isinstance(v, float):
            return v if math.isfinite(v) else {"t": "num", "v": repr(v)}
        if isinstance(v, str):
            return {"t": "str", "v": v[:MAX_STR]}
        if isinstance(v, (tuple, frozenset)):
            if depth > 4:
                return {"t": "other", "v": "(...)"}
            items = list(v) if isinstance(v, tuple) else sort_items(v)
            return {"t": "tuple", "items": [self.value(x, depth + 1) for x in items[:MAX_ITEMS]]}
        if isinstance(v, HIDDEN_TYPES):
            return {"t": "fn", "v": getattr(v, "__name__", type(v).__name__)}
        return self.ref(v)

    def ref(self, obj):
        key = id(obj)
        hid = self.ids.get(key)
        if hid is None:
            hid = self.ids[key] = len(self.ids) + 1
            self.keep_alive.append(obj)
        if hid not in self.heap and len(self.heap) < MAX_HEAP:
            self.heap[hid] = None
            self.pending.append((hid, obj))
        return {"t": "ref", "id": hid}

    def finish(self):
        while self.pending:
            hid, obj = self.pending.pop()
            self.heap[hid] = self.encode_object(obj)
        return {str(k): v for k, v in self.heap.items() if v is not None}

    def encode_object(self, o):
        if isinstance(o, list):
            return {"t": "list", "len": len(o), "items": [self.value(x) for x in o[:MAX_ITEMS]]}
        if isinstance(o, deque):
            return {"t": "deque", "len": len(o), "items": [self.value(x) for x in list(o)[:MAX_ITEMS]]}
        if isinstance(o, set):
            return {"t": "set", "len": len(o), "items": [self.value(x) for x in sort_items(o)[:MAX_ITEMS]]}
        if isinstance(o, dict):
            entries = list(o.items())[:MAX_ITEMS]
            return {
                "t": "dict",
                "cls": type(o).__name__,
                "len": len(o),
                "entries": [[self.value(k), self.value(v)] for k, v in entries],
            }
        attrs = None
        if hasattr(o, "__dict__"):
            attrs = vars(o)
        elif hasattr(type(o), "__slots__"):
            attrs = {s: getattr(o, s) for s in type(o).__slots__ if hasattr(o, s)}
        if attrs is not None:
            return {
                "t": "obj",
                "cls": type(o).__name__,
                "attrs": {k: self.value(v) for k, v in attrs.items() if not k.startswith("__")},
            }
        return {"t": "other", "v": repr(o)[:100]}


# ---------------------------------------------------------------------------
# Tracer
# ---------------------------------------------------------------------------

class StepLimit(BaseException):
    """BaseException so solutions' `except Exception` can't swallow it."""


def find_loops(tree, source_lines):
    loops = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.For, ast.While)):
            head = source_lines[node.lineno - 1].strip() if node.lineno <= len(source_lines) else ""
            loop = {
                "line": node.lineno,
                "end": node.end_lineno,
                "kind": "for" if isinstance(node, ast.For) else "while",
                "head": head.rstrip(":"),
            }
            if isinstance(node, ast.For):
                loop["targets"] = sorted({n.id for n in ast.walk(node.target) if isinstance(n, ast.Name)})
            loops.append(loop)
    return sorted(loops, key=lambda l: l["line"])


class Tracer:
    def __init__(self, loops, class_lines):
        self.steps = []
        self.enc = Encoder()
        self.frame_ids = {}
        self.next_frame_id = 1
        self.loop_counts = {}
        self.loops = {l["line"]: l for l in loops}
        self.class_lines = class_lines
        self.stdout = io.StringIO()

    def wants(self, code):
        return (
            code.co_filename == SOLUTION
            and code.co_name not in SKIP_CODE
            and code.co_firstlineno not in self.class_lines
        )

    def global_trace(self, frame, event, arg):
        if not self.wants(frame.f_code):
            return None
        if event == "call":
            self.frame_ids[id(frame)] = self.next_frame_id
            self.loop_counts[self.next_frame_id] = {}
            self.next_frame_id += 1
        return self.local_trace

    def local_trace(self, frame, event, arg):
        if event == "line":
            self.count_loops(frame)
            self.record(frame, "line")
        elif event == "return":
            self.record(frame, "return", ret=arg)
        elif event == "exception":
            self.record(frame, "exception", exc=arg)
        return self.local_trace

    def count_loops(self, frame):
        counts = self.loop_counts.setdefault(self.frame_ids.get(id(frame), 0), {})
        line = frame.f_lineno
        for start in list(counts):
            loop = self.loops[start]
            if not loop["line"] <= line <= loop["end"]:
                del counts[start]
        loop = self.loops.get(line)
        if loop:
            counts[line] = counts.get(line, 0) + 1
            for start in list(counts):
                if start != line and loop["line"] < start <= loop["end"]:
                    del counts[start]

    def stack(self, frame):
        frames = []
        f = frame
        while f is not None:
            if self.wants(f.f_code):
                frames.append(f)
            f = f.f_back
        frames.reverse()
        return frames[-MAX_FRAMES:]

    def encode_locals(self, frame):
        out = {}
        for name, v in frame.f_locals.items():
            if name.startswith("__") or name.startswith("."):
                continue
            if isinstance(v, HIDDEN_TYPES):
                continue
            out[name] = self.enc.value(v)
        return out

    def record(self, frame, event, ret=None, exc=None):
        if len(self.steps) >= MAX_STEPS:
            raise StepLimit()
        self.enc.begin()
        frames = [
            {
                "id": self.frame_ids.get(id(f), 0),
                "name": f.f_code.co_name,
                "line": f.f_lineno,
                "locals": self.encode_locals(f),
            }
            for f in self.stack(frame)
        ]
        fid = self.frame_ids.get(id(frame), 0)
        step = {
            "line": frame.f_lineno,
            "event": event,
            "frames": frames,
            "loops": [] if event == "return" else [
                {"line": l, "iter": c} for l, c in self.loop_counts.get(fid, {}).items()
            ],
        }
        if event == "return":
            step["ret"] = self.enc.value(ret)
        elif event == "exception":
            step["exc"] = f"{exc[0].__name__}: {exc[1]}"
        step["heap"] = self.enc.finish()
        step["stdout"] = self.stdout.getvalue()[-4000:]
        self.steps.append(step)

    def mark_loop_exits(self):
        """A loop header runs once more than its body (the check that ends the
        loop). Mark those final checks so the UI says "loop finished"."""
        for i, step in enumerate(self.steps[:-1]):
            loop = self.loops.get(step["line"])
            if not loop or step["event"] != "line":
                continue
            nxt = self.steps[i + 1]
            same_frame = nxt["frames"] and step["frames"] and nxt["frames"][-1]["id"] == step["frames"][-1]["id"]
            leaving = nxt["event"] == "return" or not loop["line"] <= nxt["line"] <= loop["end"]
            if same_frame and leaving:
                for entry in step["loops"]:
                    if entry["line"] == loop["line"]:
                        entry["iter"] -= 1
                        entry["done"] = True


def error_info(exc, tb):
    line = None
    while tb is not None:
        if tb.tb_frame.f_code.co_filename == SOLUTION:
            line = tb.tb_lineno
        tb = tb.tb_next
    return {"type": type(exc).__name__, "message": str(exc), "line": line}


def run(code, driver):
    try:
        tree = ast.parse(code, SOLUTION)
    except SyntaxError as e:
        return {"error": {"type": "SyntaxError", "message": e.msg, "line": e.lineno}, "steps": []}
    try:
        driver_tree = ast.parse(driver, DRIVER)
    except SyntaxError as e:
        return {"error": {"type": "SyntaxError", "message": f"in test input: {e.msg}", "line": None}, "steps": []}

    # The driver's final expression becomes the result shown in the console
    if driver_tree.body and isinstance(driver_tree.body[-1], ast.Expr):
        last = driver_tree.body[-1]
        driver_tree.body[-1] = ast.Assign(
            targets=[ast.Name(id="__result__", ctx=ast.Store())], value=last.value
        )
        ast.copy_location(driver_tree.body[-1], last)
        ast.fix_missing_locations(driver_tree)

    loops = find_loops(tree, code.splitlines())
    class_lines = {
        (n.decorator_list[0].lineno if n.decorator_list else n.lineno)
        for n in ast.walk(tree)
        if isinstance(n, ast.ClassDef)
    }
    tracer = Tracer(loops, class_lines)
    g = make_globals()
    out = {"loops": loops, "error": None, "truncated": False}

    real_stdout = sys.stdout
    sys.stdout = tracer.stdout
    sys.setrecursionlimit(2000)
    try:
        exec(compile(tree, SOLUTION, "exec"), g)
        sys.settrace(tracer.global_trace)
        exec(compile(driver_tree, DRIVER, "exec"), g)
    except StepLimit:
        out["truncated"] = True
    except Exception as e:  # noqa: BLE001 - surface any user error to the UI
        out["error"] = error_info(e, e.__traceback__)
    finally:
        sys.settrace(None)
        sys.stdout = real_stdout

    tracer.mark_loop_exits()
    out["steps"] = tracer.steps
    out["stdout"] = tracer.stdout.getvalue()[-4000:]
    if "__result__" in g and not out["truncated"] and out["error"] is None:
        try:
            out["result"] = repr(to_plain(g["__result__"]))[:2000]
        except Exception:  # noqa: BLE001
            out["result"] = "<unprintable>"
    return out


def main():
    req = json.load(sys.stdin)
    result = run(req.get("code", ""), req.get("run", ""))
    sys.stdout.write(json.dumps(result, default=repr))


if __name__ == "__main__":
    main()
