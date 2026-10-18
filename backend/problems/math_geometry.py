from ._base import p

CATEGORY = "Math & Geometry"

PROBLEMS = [
    p(48, "Rotate Image", "Medium",
      """
      Rotate an n x n matrix 90 degrees clockwise in place.
      Idea: transpose (swap across the diagonal), then reverse each row.
      """,
      """
      def rotate(matrix):
          n = len(matrix)
          # transpose: swap across the main diagonal
          for r in range(n):
              for c in range(r + 1, n):
                  matrix[r][c], matrix[c][r] = matrix[c][r], matrix[r][c]
          # then reverse each row
          for row in matrix:
              row.reverse()
          return matrix
      """,
      "rotate([[1, 2, 3], [4, 5, 6], [7, 8, 9]])",
      "[[7, 4, 1], [8, 5, 2], [9, 6, 3]]"),

    p(54, "Spiral Matrix", "Medium",
      """
      Return the matrix values in spiral order.
      Idea: walk the outer ring (top row, right column, bottom row, left
      column), shrink the four boundaries, repeat.
      """,
      """
      def spiralOrder(matrix):
          res = []
          top, bottom = 0, len(matrix)
          left, right = 0, len(matrix[0])
          while top < bottom and left < right:
              for c in range(left, right):  # top row
                  res.append(matrix[top][c])
              top += 1
              for r in range(top, bottom):  # right column
                  res.append(matrix[r][right - 1])
              right -= 1
              if not (top < bottom and left < right):
                  break
              for c in range(right - 1, left - 1, -1):  # bottom row
                  res.append(matrix[bottom - 1][c])
              bottom -= 1
              for r in range(bottom - 1, top - 1, -1):  # left column
                  res.append(matrix[r][left])
              left += 1
          return res
      """,
      "spiralOrder([[1, 2, 3, 4], [5, 6, 7, 8], [9, 10, 11, 12]])",
      "[1, 2, 3, 4, 8, 12, 11, 10, 9, 5, 6, 7]"),

    p(73, "Set Matrix Zeroes", "Medium",
      """
      If a cell is 0, zero its whole row and column.
      Idea: first record which rows/columns contain a zero, then zero them.
      (The O(1)-memory version stores these marks in the first row/column.)
      """,
      """
      def setZeroes(matrix):
          rows, cols = len(matrix), len(matrix[0])
          zero_rows, zero_cols = set(), set()
          for r in range(rows):
              for c in range(cols):
                  if matrix[r][c] == 0:
                      zero_rows.add(r)
                      zero_cols.add(c)
          for r in range(rows):
              for c in range(cols):
                  if r in zero_rows or c in zero_cols:
                      matrix[r][c] = 0
          return matrix
      """,
      "setZeroes([[1, 1, 1], [1, 0, 1], [1, 1, 1]])",
      "[[1, 0, 1], [0, 0, 0], [1, 0, 1]]"),

    p(202, "Happy Number", "Easy",
      """
      Repeatedly replace n by the sum of its digits squared. Does it reach 1?
      Idea: otherwise it loops forever, so a set detects the cycle.
      """,
      """
      def isHappy(n):
          seen = set()
          while n != 1 and n not in seen:
              seen.add(n)
              total = 0
              while n:
                  n, digit = divmod(n, 10)
                  total += digit * digit
              n = total
          return n == 1
      """,
      "isHappy(19)",
      "True"),

    p(66, "Plus One", "Easy",
      """
      Add one to a number stored as a list of digits.
      Idea: from the right, a 9 becomes 0 and carries; anything else just
      increments and we're done.
      """,
      """
      def plusOne(digits):
          for i in range(len(digits) - 1, -1, -1):
              if digits[i] < 9:
                  digits[i] += 1
                  return digits
              digits[i] = 0  # 9 + 1 = 10: write 0 and carry
          return [1] + digits
      """,
      "plusOne([1, 9, 9])",
      "[2, 0, 0]"),

    p(50, "Pow(x, n)", "Medium",
      """
      Compute x to the power n in O(log n).
      Idea: x^n = (x^(n/2))^2, times one more x when n is odd.
      """,
      """
      def myPow(x, n):
          def power(x, n):
              if n == 0:
                  return 1
              half = power(x, n // 2)
              return half * half * (x if n % 2 else 1)

          res = power(x, abs(n))
          return res if n >= 0 else 1 / res
      """,
      "myPow(2.0, 10)",
      "1024.0"),

    p(43, "Multiply Strings", "Medium",
      """
      Multiply two numbers given as strings, without converting them.
      Idea: grade-school multiplication: digit i times digit j lands in
      position i + j; push the carry to i + j + 1.
      """,
      """
      def multiply(num1, num2):
          if "0" in (num1, num2):
              return "0"
          res = [0] * (len(num1) + len(num2))
          num1, num2 = num1[::-1], num2[::-1]
          for i in range(len(num1)):
              for j in range(len(num2)):
                  res[i + j] += int(num1[i]) * int(num2[j])
                  res[i + j + 1] += res[i + j] // 10
                  res[i + j] %= 10
          res = res[::-1]
          start = 0
          while res[start] == 0:
              start += 1
          return "".join(map(str, res[start:]))
      """,
      'multiply("123", "45")',
      "'5535'"),

    p(2013, "Detect Squares", "Medium",
      """
      add(point) points; count(point) axis-aligned squares using it as a corner.
      Idea: every other point can be the opposite (diagonal) corner; the
      two remaining corners are then fixed, so multiply their counts.
      """,
      """
      class DetectSquares:
          def __init__(self):
              self.counts = defaultdict(int)  # (x, y) -> times added

          def add(self, point):
              self.counts[tuple(point)] += 1

          def count(self, point):
              px, py = point
              res = 0
              for x, y in list(self.counts):  # (x, y) = the diagonal corner
                  if abs(px - x) != abs(py - y) or x == px or y == py:
                      continue
                  res += self.counts[(x, y)] * self.counts.get((px, y), 0) * self.counts.get((x, py), 0)
              return res
      """,
      """
      ds = DetectSquares()
      ds.add([3, 10])
      ds.add([11, 2])
      ds.add([3, 2])
      out = [ds.count([11, 10]), ds.count([14, 8])]
      ds.add([11, 2])
      out.append(ds.count([11, 10]))
      out
      """,
      "[1, 0, 2]"),
]
