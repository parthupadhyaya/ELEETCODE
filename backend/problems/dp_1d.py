from ._base import p

CATEGORY = "1-D Dynamic Programming"

PROBLEMS = [
    p(70, "Climbing Stairs", "Easy",
      """
      Climb 1 or 2 steps at a time. How many ways to reach step n?
      Idea: you arrive at step i from i - 1 or i - 2, so
      dp[i] = dp[i - 1] + dp[i - 2] (Fibonacci).
      """,
      """
      def climbStairs(n):
          dp = [0] * (n + 1)
          dp[0] = dp[1] = 1
          for i in range(2, n + 1):
              dp[i] = dp[i - 1] + dp[i - 2]
          return dp[n]
      """,
      "climbStairs(6)",
      "13"),

    p(746, "Min Cost Climbing Stairs", "Easy",
      """
      Pay cost[i] to step off stair i (1 or 2 steps). Cheapest way to the top?
      Idea: dp[i] = cheapest way to stand on step i, coming from i-1 or i-2.
      """,
      """
      def minCostClimbingStairs(cost):
          n = len(cost)
          dp = [0] * (n + 1)  # dp[i] = cheapest way to reach step i
          for i in range(2, n + 1):
              dp[i] = min(dp[i - 1] + cost[i - 1], dp[i - 2] + cost[i - 2])
          return dp[n]
      """,
      "minCostClimbingStairs([1, 100, 1, 1, 1, 100, 1, 1, 100, 1])",
      "6"),

    p(198, "House Robber", "Medium",
      """
      Can't rob two adjacent houses. Most money?
      Idea: at house i either skip it (dp[i-1]) or rob it (money + dp[i-2]).
      """,
      """
      def rob(nums):
          dp = [0] * len(nums)  # dp[i] = most money from houses 0..i
          for i, money in enumerate(nums):
              skip = dp[i - 1] if i >= 1 else 0
              take = money + (dp[i - 2] if i >= 2 else 0)
              dp[i] = max(skip, take)
          return dp[-1]
      """,
      "rob([2, 7, 9, 3, 1])",
      "12"),

    p(213, "House Robber II", "Medium",
      """
      Same as House Robber, but the houses are in a circle.
      Idea: the first and last houses are neighbours, so solve twice
      (without the first, without the last) and take the better.
      """,
      """
      def rob(nums):
          if len(nums) == 1:
              return nums[0]

          def rob_line(houses):
              prev, curr = 0, 0  # best up to i - 2, best up to i - 1
              for money in houses:
                  prev, curr = curr, max(curr, prev + money)
              return curr

          return max(rob_line(nums[1:]), rob_line(nums[:-1]))
      """,
      "rob([1, 2, 3, 1])",
      "4"),

    p(5, "Longest Palindromic Substring", "Medium",
      """
      Longest substring that reads the same both ways.
      Idea: every palindrome has a center. Expand l and r outward from each
      center (odd length: one char, even length: between two chars).
      """,
      """
      def longestPalindrome(s):
          best_l, best_r = 0, 0
          for center in range(len(s)):
              for l, r in ((center, center), (center, center + 1)):
                  while l >= 0 and r < len(s) and s[l] == s[r]:
                      if r - l > best_r - best_l:
                          best_l, best_r = l, r
                      l -= 1
                      r += 1
          return s[best_l : best_r + 1]
      """,
      'longestPalindrome("babad")',
      "'bab'"),

    p(647, "Palindromic Substrings", "Medium",
      """
      Count the palindromic substrings.
      Idea: expand around every center; each successful expansion is one
      more palindrome.
      """,
      """
      def countSubstrings(s):
          count = 0
          for center in range(len(s)):
              for l, r in ((center, center), (center, center + 1)):
                  while l >= 0 and r < len(s) and s[l] == s[r]:
                      count += 1
                      l -= 1
                      r += 1
          return count
      """,
      'countSubstrings("aaa")',
      "6"),

    p(91, "Decode Ways", "Medium",
      """
      'A'=1 ... 'Z'=26. How many ways can the digit string be decoded?
      Idea: dp[i] = ways for the first i digits: take the last digit alone
      (if not '0') and/or the last two digits (if 10..26).
      """,
      """
      def numDecodings(s):
          dp = [0] * (len(s) + 1)  # dp[i] = ways to decode s[:i]
          dp[0] = 1
          for i in range(1, len(s) + 1):
              if s[i - 1] != "0":
                  dp[i] += dp[i - 1]
              if i >= 2 and 10 <= int(s[i - 2 : i]) <= 26:
                  dp[i] += dp[i - 2]
          return dp[len(s)]
      """,
      'numDecodings("2262")',
      "3"),

    p(322, "Coin Change", "Medium",
      """
      Fewest coins that make up amount (-1 if impossible).
      Idea: dp[a] = 1 + min(dp[a - coin]) over every coin that fits.
      """,
      """
      def coinChange(coins, amount):
          dp = [0] + [amount + 1] * amount  # dp[a] = fewest coins for a
          for a in range(1, amount + 1):
              for coin in coins:
                  if coin <= a:
                      dp[a] = min(dp[a], dp[a - coin] + 1)
          return dp[amount] if dp[amount] <= amount else -1
      """,
      "coinChange([1, 2, 5], 11)",
      "3"),

    p(152, "Maximum Product Subarray", "Medium",
      """
      Largest product of a contiguous subarray.
      Idea: track both the max and min product ending here; a negative
      number swaps them.
      """,
      """
      def maxProduct(nums):
          best = max(nums)
          cur_max, cur_min = 1, 1
          for n in nums:
              candidates = (n, n * cur_max, n * cur_min)
              cur_max, cur_min = max(candidates), min(candidates)
              best = max(best, cur_max)
          return best
      """,
      "maxProduct([2, 3, -2, 4])",
      "6"),

    p(139, "Word Break", "Medium",
      """
      Can s be split into dictionary words?
      Idea: dp[i] = s[i:] can be split. Work backwards: dp[i] is True if some
      word matches at i and dp[i + len(word)] is True.
      """,
      """
      def wordBreak(s, wordDict):
          dp = [False] * (len(s) + 1)  # dp[i] = s[i:] can be split
          dp[len(s)] = True
          for i in range(len(s) - 1, -1, -1):
              for w in wordDict:
                  if s[i : i + len(w)] == w and dp[i + len(w)]:
                      dp[i] = True
                      break
          return dp[0]
      """,
      'wordBreak("leetcode", ["leet", "code"])',
      "True"),

    p(300, "Longest Increasing Subsequence", "Medium",
      """
      Length of the longest strictly increasing subsequence.
      Idea: dp[i] = longest increasing subsequence starting at i
      = 1 + max dp[j] for later j with a bigger value.
      """,
      """
      def lengthOfLIS(nums):
          dp = [1] * len(nums)  # dp[i] = LIS starting at i
          for i in range(len(nums) - 1, -1, -1):
              for j in range(i + 1, len(nums)):
                  if nums[i] < nums[j]:
                      dp[i] = max(dp[i], 1 + dp[j])
          return max(dp)
      """,
      "lengthOfLIS([10, 9, 2, 5, 3, 7, 101, 18])",
      "4"),

    p(416, "Partition Equal Subset Sum", "Medium",
      """
      Can nums be split into two subsets with equal sums?
      Idea: we need a subset summing to total / 2. Track every reachable
      subset sum in a set, adding one number at a time.
      """,
      """
      def canPartition(nums):
          total = sum(nums)
          if total % 2:
              return False
          target = total // 2
          reachable = {0}  # sums some subset can make
          for n in nums:
              reachable |= {s + n for s in reachable}
              if target in reachable:
                  return True
          return False
      """,
      "canPartition([1, 5, 11, 5])",
      "True"),
]
