from ._base import p

CATEGORY = "Backtracking"

PROBLEMS = [
    p(78, "Subsets", "Medium",
      """
      Return every subset of nums.
      Idea: for each number decide include / exclude. Add, recurse, then
      undo (pop) and recurse again without it.
      """,
      """
      def subsets(nums):
          res = []
          subset = []

          def dfs(i):
              if i == len(nums):
                  res.append(subset.copy())
                  return
              subset.append(nums[i])  # include nums[i]
              dfs(i + 1)
              subset.pop()  # exclude nums[i]
              dfs(i + 1)

          dfs(0)
          return res
      """,
      "subsets([1, 2, 3])",
      "[[1, 2, 3], [1, 2], [1, 3], [1], [2, 3], [2], [3], []]"),

    p(39, "Combination Sum", "Medium",
      """
      Combinations (reusing numbers allowed) that sum to target.
      Idea: either use candidates[i] again, or move on to i + 1.
      Stop when the total overshoots.
      """,
      """
      def combinationSum(candidates, target):
          res = []
          combo = []

          def dfs(i, total):
              if total == target:
                  res.append(combo.copy())
                  return
              if i >= len(candidates) or total > target:
                  return
              combo.append(candidates[i])  # use candidates[i] (again)
              dfs(i, total + candidates[i])
              combo.pop()  # skip to the next candidate
              dfs(i + 1, total)

          dfs(0, 0)
          return res
      """,
      "combinationSum([2, 3, 6, 7], 7)",
      "[[2, 2, 3], [7]]"),

    p(40, "Combination Sum II", "Medium",
      """
      Each number used at most once, no duplicate combinations.
      Idea: sort; at each depth skip a value equal to the one just tried.
      """,
      """
      def combinationSum2(candidates, target):
          candidates.sort()
          res = []
          combo = []

          def dfs(start, total):
              if total == target:
                  res.append(combo.copy())
                  return
              for i in range(start, len(candidates)):
                  if i > start and candidates[i] == candidates[i - 1]:
                      continue  # same value already tried at this depth
                  if total + candidates[i] > target:
                      break
                  combo.append(candidates[i])
                  dfs(i + 1, total + candidates[i])
                  combo.pop()

          dfs(0, 0)
          return res
      """,
      "combinationSum2([2, 5, 2, 1, 2], 5)",
      "[[1, 2, 2], [5]]"),

    p(46, "Permutations", "Medium",
      """
      All orderings of nums.
      Idea: pick any unused number for the next slot, recurse, then un-pick.
      """,
      """
      def permute(nums):
          res = []
          perm = []
          used = [False] * len(nums)

          def dfs():
              if len(perm) == len(nums):
                  res.append(perm.copy())
                  return
              for i in range(len(nums)):
                  if used[i]:
                      continue
                  used[i] = True
                  perm.append(nums[i])
                  dfs()
                  perm.pop()
                  used[i] = False

          dfs()
          return res
      """,
      "permute([1, 2, 3])",
      "[[1, 2, 3], [1, 3, 2], [2, 1, 3], [2, 3, 1], [3, 1, 2], [3, 2, 1]]"),

    p(90, "Subsets II", "Medium",
      """
      All subsets when nums may contain duplicates (no duplicate subsets).
      Idea: sort; when excluding a value, skip all of its copies too.
      """,
      """
      def subsetsWithDup(nums):
          nums.sort()
          res = []
          subset = []

          def dfs(i):
              if i == len(nums):
                  res.append(subset.copy())
                  return
              subset.append(nums[i])
              dfs(i + 1)
              subset.pop()
              while i + 1 < len(nums) and nums[i] == nums[i + 1]:
                  i += 1  # skip every copy of nums[i]
              dfs(i + 1)

          dfs(0)
          return res
      """,
      "subsetsWithDup([1, 2, 2])",
      "[[1, 2, 2], [1, 2], [1], [2, 2], [2], []]"),

    p(79, "Word Search", "Medium",
      """
      Can word be traced through adjacent cells without reusing a cell?
      Idea: DFS from every cell; `path` holds the cells in use right now and
      is undone when backing out.
      """,
      """
      def exist(board, word):
          rows, cols = len(board), len(board[0])
          path = set()

          def dfs(r, c, i):
              if i == len(word):
                  return True
              if (r < 0 or c < 0 or r >= rows or c >= cols
                      or board[r][c] != word[i] or (r, c) in path):
                  return False
              path.add((r, c))
              found = (dfs(r + 1, c, i + 1) or dfs(r - 1, c, i + 1)
                       or dfs(r, c + 1, i + 1) or dfs(r, c - 1, i + 1))
              path.remove((r, c))
              return found

          for r in range(rows):
              for c in range(cols):
                  if dfs(r, c, 0):
                      return True
          return False
      """,
      'exist([["A", "B", "C", "E"], ["S", "F", "C", "S"], ["A", "D", "E", "E"]], "ABCCED")',
      "True"),

    p(131, "Palindrome Partitioning", "Medium",
      """
      Split s so every piece is a palindrome; return all ways.
      Idea: try every palindromic prefix s[i..j], recurse on the rest.
      """,
      """
      def partition(s):
          res = []
          part = []

          def dfs(i):
              if i == len(s):
                  res.append(part.copy())
                  return
              for j in range(i, len(s)):
                  piece = s[i : j + 1]
                  if piece == piece[::-1]:
                      part.append(piece)
                      dfs(j + 1)
                      part.pop()

          dfs(0)
          return res
      """,
      'partition("aab")',
      "[['a', 'a', 'b'], ['aa', 'b']]"),

    p(17, "Letter Combinations of a Phone Number", "Medium",
      """
      All letter strings a phone-keypad digit string could spell.
      Idea: for digit i, try each of its letters and recurse to digit i + 1.
      """,
      """
      def letterCombinations(digits):
          letters = {"2": "abc", "3": "def", "4": "ghi", "5": "jkl",
                     "6": "mno", "7": "pqrs", "8": "tuv", "9": "wxyz"}
          res = []

          def dfs(i, current):
              if len(current) == len(digits):
                  res.append(current)
                  return
              for ch in letters[digits[i]]:
                  dfs(i + 1, current + ch)

          if digits:
              dfs(0, "")
          return res
      """,
      'letterCombinations("23")',
      "['ad', 'ae', 'af', 'bd', 'be', 'bf', 'cd', 'ce', 'cf']"),

    p(51, "N-Queens", "Hard",
      """
      Place n queens so none attack each other; return all boards.
      Idea: one queen per row. Sets track used columns and both diagonals
      (r + c is constant on one, r - c on the other).
      """,
      """
      def solveNQueens(n):
          cols, pos_diag, neg_diag = set(), set(), set()
          board = [["."] * n for _ in range(n)]
          res = []

          def place(r):
              if r == n:
                  res.append(["".join(row) for row in board])
                  return
              for c in range(n):
                  if c in cols or (r + c) in pos_diag or (r - c) in neg_diag:
                      continue
                  cols.add(c)
                  pos_diag.add(r + c)
                  neg_diag.add(r - c)
                  board[r][c] = "Q"
                  place(r + 1)
                  cols.remove(c)
                  pos_diag.remove(r + c)
                  neg_diag.remove(r - c)
                  board[r][c] = "."

          place(0)
          return res
      """,
      "solveNQueens(4)",
      "[['.Q..', '...Q', 'Q...', '..Q.'], ['..Q.', 'Q...', '...Q', '.Q..']]"),
]
