"""Turns a tracer.py execution trace into an animation script with Gemini.

The raw trace is too verbose to send as-is (every step carries a full heap
snapshot), so it is first compacted into one short line of variable state per
step. Gemini is then forced to answer with JSON matching `AnimationStep`, and
the reply is validated again with Pydantic before it reaches the frontend.

Successful scripts are cached on disk (backend/.cache/animations), keyed by the
exact prompt, so the same code is only sent to Gemini once.

Needs GEMINI_API_KEY (or GOOGLE_API_KEY) in the environment or in backend/.env.
"""

import hashlib
import json
import os
import re
from pathlib import Path
from typing import Literal, Optional

from dotenv import load_dotenv
from google import genai
from google.genai import errors, types
from pydantic import BaseModel, Field, TypeAdapter, ValidationError

# Resolved next to this file so it loads whatever directory uvicorn starts in.
# Real environment variables still win over .env values.
load_dotenv(Path(__file__).with_name(".env"))

MODEL = "gemini-3.8-flash"
# Retry Gemini's transient "high demand" 503s with exponential backoff (about
# 1s, 2s, 4s plus jitter), staying well inside the frontend's 90s timeout
RETRY = types.HttpRetryOptions(attempts=4, initial_delay=1.0, max_delay=8.0, http_status_codes=[503])
CACHE_DIR = Path(__file__).with_name(".cache") / "animations"
MAX_PROMPT_STEPS = 400
MAX_VALUE_CHARS = 120
MAX_ITEMS = 12

Action = Literal[
    "highlight",     # draw attention to a variable or cells without changing them
    "compare",       # two or more values are compared
    "assign",        # a variable or cell gets a new value
    "swap",          # two cells exchange values
    "insert",        # an item is appended/pushed/added to a structure
    "remove",        # an item is popped/deleted from a structure
    "visit",         # a cell/node is marked visited or processed
    "pointer_move",  # an index/pointer variable moves (i, left, right, slow, fast, ...)
    "call",          # a function (often recursive) is entered
    "return",        # a function returns a value
    "done",          # the algorithm has produced its final answer
    "error",         # an exception was raised
]


class AnimationStep(BaseModel):
    trace_index: int = Field(description="Index of the trace step this animation belongs to (the `i` field).")
    line: int = Field(description="Source line number of that trace step.")
    action: Action = Field(description="What happens visually at this step.")
    target: str = Field(description="Variable name the action applies to, e.g. 'nums', 'seen', 'left'. Empty string if none.")
    indices: list[list[int]] = Field(
        description="Index paths into `target` that are involved: [[3]] for nums[3], [[2, 4]] for grid[2][4], "
        "[[0], [5]] for two cells. Empty list if none."
    )
    keys: list[str] = Field(description="Dict keys or set members involved, as Python literals. Empty list if none.")
    value: Optional[str] = Field(description="New or relevant value as a short Python literal, or null.")
    narration: str = Field(description="One short sentence explaining what happens and why, for a learner.")


AnimationScript = TypeAdapter(list[AnimationStep])

SYSTEM_PROMPT = """\
You turn Python execution traces into animation scripts for an algorithm visualizer.

You receive the solution code with line numbers and a list of trace steps. Each step has:
  i      step index
  line   line about to execute (or the line returning/raising)
  event  "line", "return" or "exception"
  fn     current function, depth = call-stack depth
  vars   locals of the current function as short Python reprs
  ret / exc  return value or exception, when present

Produce animation steps in increasing trace_index order. Rules:
- Only use trace_index values that appear in the input, and copy that step's line.
- Skip steps where nothing meaningful changes; merge repetitive setup into one step.
  A loop moving to its next element is always meaningful.
- Iteration: every time a for loop takes its next element from a list, tuple, string
  or row of a grid (for x in nums, for i, x in enumerate(nums), for c in s, for row in
  grid, or for i in range(len(nums)) followed by nums[i]), emit a "visit" step at the
  first trace step whose vars show the new loop value. Its target is the container
  being iterated (nums, not x) and indices is [[k]], k = that element's 0-based
  position. Find k by counting iterations, never by searching for the value, since
  values can repeat. Emit one per iteration; never skip or merge them. For dicts and
  sets, put the current key in keys and leave indices empty. Anything else that changes
  in the same iteration (like a running total) gets its own step as usual.
- Prefer concrete actions (compare, swap, assign, insert, remove, visit, pointer_move)
  over "highlight". Use the variable names exactly as they appear in vars.
- indices are index paths into the target container; keys are dict keys or set members.
- Narration is one plain-English sentence aimed at someone learning the algorithm:
  say what happens and why, using the actual values.
- If the trace ends with a result, finish with a "done" step; if it raised, an "error" step.
"""


class GeminiError(Exception):
    """Raised when an animation script can't be produced."""


_client = None


def client():
    # Created lazily so the server starts (and /api/trace works) without a key
    global _client
    if _client is None:
        try:
            _client = genai.Client(http_options=types.HttpOptions(retry_options=RETRY))
        except ValueError as e:
            raise GeminiError("Set GEMINI_API_KEY to enable AI animation scripts.") from e
    return _client


# ---------------------------------------------------------------------------
# Trace compaction
# ---------------------------------------------------------------------------

def show(v, heap, depth=0):
    """Encoded tracer value -> short Python-like text."""
    if v is None or isinstance(v, bool):
        return repr(v)
    if isinstance(v, (int, float)):
        return repr(v)
    t = v.get("t")
    if t == "str":
        return repr(v["v"])
    if t in ("num", "other"):
        return v["v"]
    if t == "fn":
        return f"<fn {v['v']}>"
    if t == "tuple":
        inner = ", ".join(show(x, heap, depth + 1) for x in v["items"][:MAX_ITEMS])
        return f"({inner}{',' if len(v['items']) == 1 else ''})"
    if t == "ref":
        obj = heap.get(str(v["id"]))
        return show_object(obj, heap, depth) if obj else "..."
    return "?"


def show_object(obj, heap, depth):
    if depth >= 2:
        return "..."
    t = obj["t"]

    def items(seq):
        text = ", ".join(show(x, heap, depth + 1) for x in seq[:MAX_ITEMS])
        return text + (", ..." if obj["len"] > MAX_ITEMS else "")

    if t == "list":
        return f"[{items(obj['items'])}]"
    if t == "deque":
        return f"deque([{items(obj['items'])}])"
    if t == "set":
        return f"{{{items(obj['items'])}}}" if obj["len"] else "set()"
    if t == "dict":
        pairs = ", ".join(
            f"{show(k, heap, depth + 1)}: {show(val, heap, depth + 1)}" for k, val in obj["entries"][:MAX_ITEMS]
        )
        return f"{{{pairs}{', ...' if obj['len'] > MAX_ITEMS else ''}}}"
    if t == "obj":
        attrs = ", ".join(f"{k}={show_attr(a, heap, depth)}" for k, a in obj["attrs"].items())
        return f"{obj['cls']}({attrs})"
    return obj.get("v", "?")


def show_attr(a, heap, depth):
    # Node-like objects (ListNode.next, TreeNode.left): name the linked object's
    # class instead of expanding the whole structure behind it
    if isinstance(a, dict) and a.get("t") == "ref":
        target = heap.get(str(a["id"]))
        if target and target["t"] == "obj":
            return f"<{target['cls']}>"
    return show(a, heap, depth + 1)


def compact_step(i, step):
    frame = step["frames"][-1] if step["frames"] else {"name": "?", "locals": {}}
    heap = step.get("heap", {})
    out = {
        "i": i,
        "line": step["line"],
        "event": step["event"],
        "fn": frame["name"],
        "depth": len(step["frames"]),
        "vars": {name: show(v, heap)[:MAX_VALUE_CHARS] for name, v in frame["locals"].items()},
    }
    if "ret" in step:
        out["ret"] = show(step["ret"], heap)[:MAX_VALUE_CHARS]
    if "exc" in step:
        out["exc"] = step["exc"]
    return out


def compact_trace(trace):
    steps = trace["steps"]
    # Long traces are sampled evenly; indices stay the original ones
    if len(steps) > MAX_PROMPT_STEPS:
        stride = len(steps) / MAX_PROMPT_STEPS
        picked = sorted({int(k * stride) for k in range(MAX_PROMPT_STEPS)} | {len(steps) - 1})
    else:
        picked = range(len(steps))
    return [compact_step(i, steps[i]) for i in picked]


def strip_addresses(text):
    # "<Node object at 0x0000023E2D122950>" -> "<Node object>": the address
    # differs every run, which would make every prompt (and cache key) unique
    return re.sub(r" at 0x[0-9a-fA-F]+", "", str(text))


def build_prompt(code, trace):
    numbered = "\n".join(f"{n:>3} | {line}" for n, line in enumerate(code.splitlines(), 1))
    parts = [
        f"Solution code:\n{numbered}",
        f"Trace ({len(trace['steps'])} steps total):\n"
        + "\n".join(json.dumps(s, ensure_ascii=False) for s in compact_trace(trace)),
    ]
    if trace.get("result") is not None:
        parts.append(f"Final result: {strip_addresses(trace['result'])}")
    if trace.get("error"):
        parts.append(f"Error: {trace['error']['type']}: {strip_addresses(trace['error']['message'])}")
    if trace.get("truncated"):
        parts.append("The trace was cut off at the step limit before the code finished.")
    return "\n\n".join(parts)


# ---------------------------------------------------------------------------
# Gemini call
# ---------------------------------------------------------------------------

def build_animation(code, trace):
    """Return a validated list[AnimationStep] for a tracer.py trace."""
    prompt = build_prompt(code, trace)
    # The model and system prompt are part of the key, so changing either one
    # skips older cached scripts instead of serving them
    key = hashlib.sha256("\0".join((MODEL, SYSTEM_PROMPT, prompt)).encode()).hexdigest()
    steps = cache_get(key)
    if steps is None:
        steps = generate(prompt)
        cache_put(key, steps)

    # Drop anything pointing outside the trace, and keep the script in order
    total = len(trace["steps"])
    return sorted((s for s in steps if 0 <= s.trace_index < total), key=lambda s: s.trace_index)


def cache_get(key):
    try:
        return AnimationScript.validate_json((CACHE_DIR / f"{key}.json").read_bytes())
    except (OSError, ValidationError):
        return None  # missing or unreadable: treat as a miss


def cache_put(key, steps):
    # Write to a temp file and rename, so a concurrent read never sees half a file
    try:
        CACHE_DIR.mkdir(parents=True, exist_ok=True)
        tmp = CACHE_DIR / f"{key}.{os.getpid()}.tmp"
        tmp.write_bytes(AnimationScript.dump_json(steps))
        os.replace(tmp, CACHE_DIR / f"{key}.json")
    except OSError:
        pass  # caching is best-effort


def generate(prompt):
    """Ask Gemini for an animation script and validate it."""
    try:
        response = client().models.generate_content(
            model=MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_PROMPT,
                response_mime_type="application/json",
                response_schema=list[AnimationStep],
                temperature=0.2,
            ),
        )
    except errors.APIError as e:
        raise GeminiError(f"Gemini API error {e.code}: {e.message}") from e

    try:
        steps = response.parsed if response.parsed is not None else AnimationScript.validate_json(response.text or "")
        return AnimationScript.validate_python(steps)
    except ValidationError as e:
        raise GeminiError(f"Gemini returned JSON that doesn't match the animation schema: {e}") from e
