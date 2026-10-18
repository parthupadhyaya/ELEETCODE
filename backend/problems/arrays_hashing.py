from ._base import p

CATEGORY = "Arrays & Hashing"

PROBLEMS = [
    p(217, "Contains Duplicate", "Easy",
      """
      Return True if any value appears at least twice in nums.
      Idea: remember every number in a set; seeing one again means a duplicate.
      """,
      """
      def containsDuplicate(nums):
          seen = set()
          for n in nums:
              if n in seen:
                  return True
              seen.add(n)
          return False
      """,
      "containsDuplicate([1, 2, 3, 4, 2])",
      "True"),

    p(242, "Valid Anagram", "Easy",
      """
      Return True if t is a rearrangement of the letters of s.
      Idea: count letters of s in a hashmap, then use the counts up with t.
      """,
      """
      def isAnagram(s, t):
          if len(s) != len(t):
              return False
          count = {}
          for ch in s:
              count[ch] = count.get(ch, 0) + 1
          for ch in t:
              if count.get(ch, 0) == 0:
                  return False
              count[ch] -= 1
          return True
      """,
      'isAnagram("anagram", "nagaram")',
      "True"),

    p(1, "Two Sum", "Easy",
      """
      Return the indexes of the two numbers that add up to target.
      Idea: for each number, check whether its complement (target - n) was
      already seen. A hashmap maps value -> index for O(1) lookups.
      """,
      """
      def twoSum(nums, target):
          seen = {}  # value -> index
          for i, n in enumerate(nums):
              diff = target - n
              if diff in seen:
                  return [seen[diff], i]
              seen[n] = i
      """,
      "twoSum([3, 4, 5, 6], 11)",
      "[2, 3]"),

    p(49, "Group Anagrams", "Medium",
      """
      Group words that are anagrams of each other.
      Idea: anagrams share the same sorted letters, so use that as a hashmap key.
      """,
      """
      def groupAnagrams(strs):
          groups = defaultdict(list)
          for s in strs:
              key = "".join(sorted(s))
              groups[key].append(s)
          return list(groups.values())
      """,
      'groupAnagrams(["eat", "tea", "tan", "ate", "nat", "bat"])',
      "[['eat', 'tea', 'ate'], ['tan', 'nat'], ['bat']]"),

    p(347, "Top K Frequent Elements", "Medium",
      """
      Return the k most frequent numbers.
      Idea: count with a hashmap, then bucket numbers by frequency
      (bucket[i] = numbers seen i times) and read buckets from the top.
      """,
      """
      def topKFrequent(nums, k):
          count = {}
          for n in nums:
              count[n] = count.get(n, 0) + 1
          buckets = [[] for _ in range(len(nums) + 1)]
          for n, c in count.items():
              buckets[c].append(n)
          res = []
          for freq in range(len(buckets) - 1, 0, -1):
              for n in buckets[freq]:
                  res.append(n)
                  if len(res) == k:
                      return res
          return res
      """,
      "topKFrequent([1, 1, 1, 2, 2, 3], 2)",
      "[1, 2]"),

    p(271, "Encode and Decode Strings", "Medium",
      """
      Encode a list of strings into one string and decode it back.
      Idea: prefix each word with its length and a '#', so the decoder knows
      exactly how many characters to read even if words contain '#'.
      """,
      """
      def encode(strs):
          res = ""
          for s in strs:
              res += str(len(s)) + "#" + s
          return res

      def decode(s):
          res, i = [], 0
          while i < len(s):
              j = i
              while s[j] != "#":
                  j += 1
              length = int(s[i:j])
              res.append(s[j + 1 : j + 1 + length])
              i = j + 1 + length
          return res
      """,
      'decode(encode(["neet", "code", "you"]))',
      "['neet', 'code', 'you']"),

    p(238, "Product of Array Except Self", "Medium",
      """
      res[i] = product of every number except nums[i], without division.
      Idea: one pass left-to-right stores the prefix product, a second pass
      right-to-left multiplies in the suffix product.
      """,
      """
      def productExceptSelf(nums):
          res = [1] * len(nums)
          prefix = 1
          for i in range(len(nums)):
              res[i] = prefix
              prefix *= nums[i]
          suffix = 1
          for i in range(len(nums) - 1, -1, -1):
              res[i] *= suffix
              suffix *= nums[i]
          return res
      """,
      "productExceptSelf([1, 2, 3, 4])",
      "[24, 12, 8, 6]"),

    p(36, "Valid Sudoku", "Medium",
      """
      Check that no row, column or 3x3 box repeats a digit.
      Idea: one set per row, column and box; box id is (r // 3, c // 3).
      """,
      """
      def isValidSudoku(board):
          rows = defaultdict(set)
          cols = defaultdict(set)
          boxes = defaultdict(set)
          for r in range(9):
              for c in range(9):
                  val = board[r][c]
                  if val == ".":
                      continue
                  box = (r // 3, c // 3)
                  if val in rows[r] or val in cols[c] or val in boxes[box]:
                      return False
                  rows[r].add(val)
                  cols[c].add(val)
                  boxes[box].add(val)
          return True
      """,
      """
      isValidSudoku([
          ["8","3",".",".","7",".",".",".","."],
          ["6",".",".","1","9","5",".",".","."],
          [".","9","8",".",".",".",".","6","."],
          ["8",".",".",".","6",".",".",".","3"],
          ["4",".",".","8",".","3",".",".","1"],
          ["7",".",".",".","2",".",".",".","6"],
          [".","6",".",".",".",".","2","8","."],
          [".",".",".","4","1","9",".",".","5"],
          [".",".",".",".","8",".",".","7","9"],
      ])
      """,
      "False"),

    p(128, "Longest Consecutive Sequence", "Medium",
      """
      Length of the longest run of consecutive integers (any order) in O(n).
      Idea: put everything in a set; only start counting from numbers that
      have no left neighbour (n - 1 missing), so each run is walked once.
      """,
      """
      def longestConsecutive(nums):
          num_set = set(nums)
          longest = 0
          for n in num_set:
              if n - 1 not in num_set:
                  length = 1
                  while n + length in num_set:
                      length += 1
                  longest = max(longest, length)
          return longest
      """,
      "longestConsecutive([100, 4, 200, 1, 3, 2])",
      "4"),
]
