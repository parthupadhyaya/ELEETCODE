from textwrap import dedent


def p(num, title, difficulty, description, code, run, expect=None):
    """One problem. `code` is the solution shown in the editor, `run` is the
    test driver whose last expression is the result, `expect` is repr() of
    the correct result (checked by test_problems.py)."""
    return {
        "num": num,
        "title": title,
        "difficulty": difficulty,
        "description": dedent(description).strip(),
        "code": dedent(code).strip("\n") + "\n",
        "run": dedent(run).strip() + "\n",
        "expect": expect,
    }
