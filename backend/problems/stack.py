from ._base import p

CATEGORY = "Stack"

PROBLEMS = [
    p(20, "Valid Parentheses", "Easy",
      """
      Are the brackets balanced and correctly nested?
      Idea: push openers; each closer must match the opener on top.
      """,
      """
      def isValid(s):
          stack = []
          pairs = {")": "(", "]": "[", "}": "{"}
          for ch in s:
              if ch in pairs:
                  if stack and stack[-1] == pairs[ch]:
                      stack.pop()
                  else:
                      return False
              else:
                  stack.append(ch)
          return not stack
      """,
      'isValid("([{}])()")',
      "True"),

    p(155, "Min Stack", "Medium",
      """
      A stack that also returns its minimum in O(1).
      Idea: a second stack stores the minimum at each height.
      """,
      """
      class MinStack:
          def __init__(self):
              self.stack = []
              self.min_stack = []

          def push(self, val):
              self.stack.append(val)
              val = min(val, self.min_stack[-1] if self.min_stack else val)
              self.min_stack.append(val)

          def pop(self):
              self.stack.pop()
              self.min_stack.pop()

          def top(self):
              return self.stack[-1]

          def getMin(self):
              return self.min_stack[-1]
      """,
      """
      s = MinStack()
      s.push(-2)
      s.push(0)
      s.push(-3)
      out = [s.getMin()]
      s.pop()
      out.append(s.top())
      out.append(s.getMin())
      out
      """,
      "[-3, 0, -2]"),

    p(150, "Evaluate Reverse Polish Notation", "Medium",
      """
      Evaluate a postfix expression like ["2", "1", "+", "3", "*"].
      Idea: push numbers; an operator pops two, applies, pushes the result.
      """,
      """
      def evalRPN(tokens):
          stack = []
          for tok in tokens:
              if tok in "+-*/":
                  b = stack.pop()
                  a = stack.pop()
                  if tok == "+":
                      stack.append(a + b)
                  elif tok == "-":
                      stack.append(a - b)
                  elif tok == "*":
                      stack.append(a * b)
                  else:
                      stack.append(int(a / b))
              else:
                  stack.append(int(tok))
          return stack[0]
      """,
      'evalRPN(["4", "13", "5", "/", "+"])',
      "6"),

    p(22, "Generate Parentheses", "Medium",
      """
      All combinations of n pairs of well-formed parentheses.
      Idea: backtrack. Add "(" while open < n; add ")" while close < open.
      """,
      """
      def generateParenthesis(n):
          res = []
          stack = []

          def backtrack(open_count, close_count):
              if open_count == close_count == n:
                  res.append("".join(stack))
                  return
              if open_count < n:
                  stack.append("(")
                  backtrack(open_count + 1, close_count)
                  stack.pop()
              if close_count < open_count:
                  stack.append(")")
                  backtrack(open_count, close_count + 1)
                  stack.pop()

          backtrack(0, 0)
          return res
      """,
      "generateParenthesis(3)",
      "['((()))', '(()())', '(())()', '()(())', '()()()']"),

    p(739, "Daily Temperatures", "Medium",
      """
      For each day, how many days until a warmer temperature?
      Idea: a monotonic stack of days still waiting. A warmer day pops
      everything colder and fills in their answers.
      """,
      """
      def dailyTemperatures(temperatures):
          res = [0] * len(temperatures)
          stack = []  # indexes still waiting for a warmer day
          for i, t in enumerate(temperatures):
              while stack and temperatures[stack[-1]] < t:
                  j = stack.pop()
                  res[j] = i - j
              stack.append(i)
          return res
      """,
      "dailyTemperatures([73, 74, 75, 71, 69, 72, 76, 73])",
      "[1, 1, 4, 2, 1, 1, 0, 0]"),

    p(853, "Car Fleet", "Medium",
      """
      Cars can't pass each other; a caught-up car joins that fleet.
      How many fleets reach the target?
      Idea: process cars closest to the target first; a car whose arrival
      time is later than the fleet ahead starts a new fleet.
      """,
      """
      def carFleet(target, position, speed):
          cars = sorted(zip(position, speed), reverse=True)
          stack = []  # arrival time of each fleet
          for pos, spd in cars:
              time = (target - pos) / spd
              if not stack or time > stack[-1]:
                  stack.append(time)
          return len(stack)
      """,
      "carFleet(12, [10, 8, 0, 5, 3], [2, 4, 1, 1, 3])",
      "3"),

    p(84, "Largest Rectangle in Histogram", "Hard",
      """
      Largest rectangle that fits under the histogram.
      Idea: keep (start, height) in an increasing stack. A shorter bar pops
      taller ones (their rectangle ends here) and inherits their start.
      """,
      """
      def largestRectangleArea(heights):
          best = 0
          stack = []  # (start index, height)
          for i, h in enumerate(heights):
              start = i
              while stack and stack[-1][1] > h:
                  idx, height = stack.pop()
                  best = max(best, height * (i - idx))
                  start = idx
              stack.append((start, h))
          for idx, height in stack:
              best = max(best, height * (len(heights) - idx))
          return best
      """,
      "largestRectangleArea([2, 1, 5, 6, 2, 3])",
      "10"),
]
