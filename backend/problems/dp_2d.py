from ._base import p

CATEGORY = "2-D Dynamic Programming"

PROBLEMS = [
    p(62, "Unique Paths", "Medium",
      """
      Robot moves only right or down. How many paths across an m x n grid?
      Idea: paths into a cell = paths from above + paths from the left.
      """,
      """
      def uniquePaths(m, n):
          dp = [[1] * n for _ in range(m)]
          for r in range(1, m):
              for c in range(1, n):
                  dp[r][c] = dp[r - 1][c] + dp[r][c - 1]
          return dp[m - 1][n - 1]
      """,
      "uniquePaths(3, 4)",
      "10"),

    p(1143, "Longest Common Subsequence", "Medium",
      """
      Length of the longest subsequence shared by both strings.
      Idea: dp[i][j] = LCS of text1[i:] and text2[j:]. Matching letters
      extend the diagonal; otherwise take the better of skipping one letter.
      """,
      """
      def longestCommonSubsequence(text1, text2):
          dp = [[0] * (len(text2) + 1) for _ in range(len(text1) + 1)]
          for i in range(len(text1) - 1, -1, -1):
              for j in range(len(text2) - 1, -1, -1):
                  if text1[i] == text2[j]:
                      dp[i][j] = 1 + dp[i + 1][j + 1]
                  else:
                      dp[i][j] = max(dp[i + 1][j], dp[i][j + 1])
          return dp[0][0]
      """,
      'longestCommonSubsequence("abcde", "ace")',
      "3"),

    p(309, "Best Time to Buy and Sell Stock with Cooldown", "Medium",
      """
      Unlimited trades, but after selling you must rest one day.
      Idea: a state machine. Each day you are holding, just sold, or resting;
      compute each state's best profit from yesterday's states.
      """,
      """
      def maxProfit(prices):
          hold, sold, rest = float("-inf"), 0, 0
          for price in prices:
              hold, sold, rest = (
                  max(hold, rest - price),  # keep holding, or buy today
                  hold + price,             # sell what we held
                  max(rest, sold),          # cooldown / do nothing
              )
          return max(sold, rest)
      """,
      "maxProfit([1, 2, 3, 0, 2])",
      "3"),

    p(518, "Coin Change II", "Medium",
      """
      Number of coin combinations that make amount.
      Idea: process one coin type at a time so each combination is counted
      once: dp[a] += dp[a - coin].
      """,
      """
      def change(amount, coins):
          dp = [0] * (amount + 1)  # dp[a] = ways to make a
          dp[0] = 1
          for coin in coins:
              for a in range(coin, amount + 1):
                  dp[a] += dp[a - coin]
          return dp[amount]
      """,
      "change(5, [1, 2, 5])",
      "4"),

    p(494, "Target Sum", "Medium",
      """
      Put + or - before each number. How many ways reach target?
      Idea: a hashmap of running sum -> ways; each number branches every
      sum into sum + n and sum - n.
      """,
      """
      def findTargetSumWays(nums, target):
          ways = {0: 1}  # running sum -> number of ways to reach it
          for n in nums:
              nxt = defaultdict(int)
              for total, count in ways.items():
                  nxt[total + n] += count
                  nxt[total - n] += count
              ways = nxt
          return ways.get(target, 0)
      """,
      "findTargetSumWays([1, 1, 1, 1, 1], 3)",
      "5"),

    p(97, "Interleaving String", "Medium",
      """
      Is s3 formed by interleaving s1 and s2?
      Idea: dp[i][j] = s1[i:] and s2[j:] can form s3[i + j:]. Take the next
      char from s1 or from s2 if it matches s3.
      """,
      """
      def isInterleave(s1, s2, s3):
          if len(s1) + len(s2) != len(s3):
              return False
          dp = [[False] * (len(s2) + 1) for _ in range(len(s1) + 1)]
          dp[len(s1)][len(s2)] = True
          for i in range(len(s1), -1, -1):
              for j in range(len(s2), -1, -1):
                  if i < len(s1) and s1[i] == s3[i + j] and dp[i + 1][j]:
                      dp[i][j] = True
                  if j < len(s2) and s2[j] == s3[i + j] and dp[i][j + 1]:
                      dp[i][j] = True
          return dp[0][0]
      """,
      'isInterleave("aab", "axy", "aaxaby")',
      "True"),

    p(329, "Longest Increasing Path in a Matrix", "Hard",
      """
      Longest strictly increasing path moving up/down/left/right.
      Idea: DFS from each cell with memoization; a cell's answer never
      changes, so compute it once.
      """,
      """
      def longestIncreasingPath(matrix):
          rows, cols = len(matrix), len(matrix[0])
          memo = {}  # (r, c) -> longest path starting there

          def dfs(r, c, prev):
              if r < 0 or c < 0 or r >= rows or c >= cols or matrix[r][c] <= prev:
                  return 0
              if (r, c) in memo:
                  return memo[(r, c)]
              best = 1
              for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                  best = max(best, 1 + dfs(r + dr, c + dc, matrix[r][c]))
              memo[(r, c)] = best
              return best

          longest = 0
          for r in range(rows):
              for c in range(cols):
                  longest = max(longest, dfs(r, c, -1))
          return longest
      """,
      "longestIncreasingPath([[9, 9, 4], [6, 6, 8], [2, 1, 1]])",
      "4"),

    p(115, "Distinct Subsequences", "Hard",
      """
      How many distinct subsequences of s equal t?
      Idea: dp[i][j] = ways s[i:] forms t[j:]. Always may skip s[i]; if
      s[i] == t[j] you may also use it.
      """,
      """
      def numDistinct(s, t):
          dp = [[0] * (len(t) + 1) for _ in range(len(s) + 1)]
          for i in range(len(s) + 1):
              dp[i][len(t)] = 1  # empty t: exactly one way
          for i in range(len(s) - 1, -1, -1):
              for j in range(len(t) - 1, -1, -1):
                  dp[i][j] = dp[i + 1][j]
                  if s[i] == t[j]:
                      dp[i][j] += dp[i + 1][j + 1]
          return dp[0][0]
      """,
      'numDistinct("rabbbit", "rabbit")',
      "3"),

    p(72, "Edit Distance", "Medium",
      """
      Fewest inserts/deletes/replaces to turn word1 into word2.
      Idea: dp[i][j] = edits for word1[i:] -> word2[j:]. Equal letters cost
      nothing; otherwise 1 + best of delete, insert, replace.
      """,
      """
      def minDistance(word1, word2):
          m, n = len(word1), len(word2)
          dp = [[0] * (n + 1) for _ in range(m + 1)]
          for i in range(m + 1):
              dp[i][n] = m - i
          for j in range(n + 1):
              dp[m][j] = n - j
          for i in range(m - 1, -1, -1):
              for j in range(n - 1, -1, -1):
                  if word1[i] == word2[j]:
                      dp[i][j] = dp[i + 1][j + 1]
                  else:
                      dp[i][j] = 1 + min(dp[i + 1][j],      # delete
                                         dp[i][j + 1],      # insert
                                         dp[i + 1][j + 1])  # replace
          return dp[0][0]
      """,
      'minDistance("horse", "ros")',
      "3"),

    p(312, "Burst Balloons", "Hard",
      """
      Bursting balloon i earns left * i * right. Max coins?
      Idea: choose which balloon in (l, r) bursts LAST; its neighbours are
      then exactly l and r. dp[l][r] = best over that choice.
      """,
      """
      def maxCoins(nums):
          nums = [1] + nums + [1]
          n = len(nums)
          dp = [[0] * n for _ in range(n)]  # dp[l][r]: best for balloons between l and r
          for length in range(2, n):
              for l in range(0, n - length):
                  r = l + length
                  for last in range(l + 1, r):  # balloon burst last in (l, r)
                      coins = nums[l] * nums[last] * nums[r] + dp[l][last] + dp[last][r]
                      dp[l][r] = max(dp[l][r], coins)
          return dp[0][n - 1]
      """,
      "maxCoins([3, 1, 5, 8])",
      "167"),

    p(10, "Regular Expression Matching", "Hard",
      """
      Match s against p where '.' is any char and 'x*' is zero or more x.
      Idea: memoized DFS on (i, j). With a '*' next, either skip "x*" or
      use it for one char and stay on the same pattern position.
      """,
      """
      def isMatch(s, p):
          memo = {}

          def dfs(i, j):  # does s[i:] match p[j:]?
              if (i, j) in memo:
                  return memo[(i, j)]
              if j == len(p):
                  return i == len(s)
              first = i < len(s) and p[j] in (s[i], ".")
              if j + 1 < len(p) and p[j + 1] == "*":
                  res = dfs(i, j + 2) or (first and dfs(i + 1, j))
              else:
                  res = first and dfs(i + 1, j + 1)
              memo[(i, j)] = res
              return res

          return dfs(0, 0)
      """,
      'isMatch("aab", "c*a*b")',
      "True"),
]
