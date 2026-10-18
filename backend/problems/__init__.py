"""The NeetCode 150, grouped in NeetCode roadmap order."""

import re

from . import (
    advanced_graphs, arrays_hashing, backtracking, binary_search,
    bit_manipulation, dp_1d, dp_2d, graphs, greedy, heap, intervals,
    linked_list, math_geometry, sliding_window, stack, trees, tries,
    two_pointers,
)

_MODULES = [
    arrays_hashing, two_pointers, sliding_window, stack, binary_search,
    linked_list, trees, heap, backtracking, tries, graphs, advanced_graphs,
    dp_1d, dp_2d, greedy, intervals, math_geometry, bit_manipulation,
]


def _slug(title):
    return re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")


PROBLEMS = []
for _module in _MODULES:
    for _problem in _module.PROBLEMS:
        PROBLEMS.append({"id": _slug(_problem["title"]), "category": _module.CATEGORY, **_problem})

PROBLEMS_BY_ID = {p["id"]: p for p in PROBLEMS}
assert len(PROBLEMS_BY_ID) == len(PROBLEMS), "duplicate problem ids"
