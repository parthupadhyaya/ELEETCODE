from ._base import p

CATEGORY = "Sliding Window"

PROBLEMS = [
    p(121, "Best Time to Buy and Sell Stock", "Easy",
      """
      Max profit from one buy then one later sell.
      Idea: l is the cheapest day so far; r scans forward. A new low moves l.
      """,
      """
      def maxProfit(prices):
          l = 0
          best = 0
          for r in range(1, len(prices)):
              if prices[r] < prices[l]:
                  l = r
              else:
                  best = max(best, prices[r] - prices[l])
          return best
      """,
      "maxProfit([7, 1, 5, 3, 6, 4])",
      "5"),

    p(3, "Longest Substring Without Repeating Characters", "Medium",
      """
      Length of the longest substring with no repeated characters.
      Idea: grow the window with r; while s[r] is already inside, shrink
      from l. The set holds the window's characters.
      """,
      """
      def lengthOfLongestSubstring(s):
          window = set()
          l = 0
          best = 0
          for r in range(len(s)):
              while s[r] in window:
                  window.remove(s[l])
                  l += 1
              window.add(s[r])
              best = max(best, r - l + 1)
          return best
      """,
      'lengthOfLongestSubstring("abcabcbb")',
      "3"),

    p(424, "Longest Repeating Character Replacement", "Medium",
      """
      Replace up to k characters to make the longest run of one letter.
      Idea: a window is valid when (size - count of its most common letter)
      <= k. Grow with r, shrink with l when invalid.
      """,
      """
      def characterReplacement(s, k):
          count = {}
          l = 0
          max_freq = 0
          best = 0
          for r in range(len(s)):
              count[s[r]] = count.get(s[r], 0) + 1
              max_freq = max(max_freq, count[s[r]])
              while (r - l + 1) - max_freq > k:
                  count[s[l]] -= 1
                  l += 1
              best = max(best, r - l + 1)
          return best
      """,
      'characterReplacement("AABABBA", 1)',
      "4"),

    p(567, "Permutation in String", "Medium",
      """
      Does s2 contain some permutation of s1?
      Idea: slide a window of len(s1) over s2 and compare letter counts.
      """,
      """
      def checkInclusion(s1, s2):
          if len(s1) > len(s2):
              return False
          need = Counter(s1)
          window = Counter()
          l = 0
          for r in range(len(s2)):
              window[s2[r]] += 1
              if r - l + 1 > len(s1):
                  window[s2[l]] -= 1
                  if window[s2[l]] == 0:
                      del window[s2[l]]
                  l += 1
              if window == need:
                  return True
          return False
      """,
      'checkInclusion("ab", "eidbaooo")',
      "True"),

    p(76, "Minimum Window Substring", "Hard",
      """
      Smallest substring of s containing every character of t.
      Idea: expand r until the window has everything (have == required),
      then shrink l as far as possible while recording the best window.
      """,
      """
      def minWindow(s, t):
          need = Counter(t)
          window = {}
          have, required = 0, len(need)
          best, best_len = (-1, -1), float("inf")
          l = 0
          for r in range(len(s)):
              ch = s[r]
              window[ch] = window.get(ch, 0) + 1
              if ch in need and window[ch] == need[ch]:
                  have += 1
              while have == required:
                  if r - l + 1 < best_len:
                      best, best_len = (l, r), r - l + 1
                  window[s[l]] -= 1
                  if s[l] in need and window[s[l]] < need[s[l]]:
                      have -= 1
                  l += 1
          l, r = best
          return s[l : r + 1] if best_len != float("inf") else ""
      """,
      'minWindow("ADOBECODEBANC", "ABC")',
      "'BANC'"),

    p(239, "Sliding Window Maximum", "Hard",
      """
      Max of every window of size k.
      Idea: a deque of indexes whose values are decreasing; the front is
      always the current max. Drop smaller values from the back as you go.
      """,
      """
      def maxSlidingWindow(nums, k):
          q = deque()  # indexes, values decreasing
          res = []
          l = 0
          for r in range(len(nums)):
              while q and nums[q[-1]] < nums[r]:
                  q.pop()
              q.append(r)
              if l > q[0]:
                  q.popleft()
              if r + 1 >= k:
                  res.append(nums[q[0]])
                  l += 1
          return res
      """,
      "maxSlidingWindow([1, 3, -1, -3, 5, 3, 6, 7], 3)",
      "[3, 3, 5, 5, 6, 7]"),
]
