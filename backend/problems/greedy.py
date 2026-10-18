from ._base import p

CATEGORY = "Greedy"

PROBLEMS = [
    p(53, "Maximum Subarray", "Medium",
      """
      Largest sum of a contiguous subarray.
      Idea: Kadane's algorithm: a negative running sum can only hurt, so
      drop it and start fresh.
      """,
      """
      def maxSubArray(nums):
          best = nums[0]
          current = 0
          for n in nums:
              current = max(current, 0) + n  # drop a negative running sum
              best = max(best, current)
          return best
      """,
      "maxSubArray([-2, 1, -3, 4, -1, 2, 1, -5, 4])",
      "6"),

    p(55, "Jump Game", "Medium",
      """
      nums[i] is the max jump from i. Can you reach the last index?
      Idea: walk backwards moving the goal: if i can reach the goal, then
      reaching i is enough.
      """,
      """
      def canJump(nums):
          goal = len(nums) - 1
          for i in range(len(nums) - 1, -1, -1):
              if i + nums[i] >= goal:
                  goal = i  # reaching i is now enough
          return goal == 0
      """,
      "canJump([2, 3, 1, 1, 4])",
      "True"),

    p(45, "Jump Game II", "Medium",
      """
      Fewest jumps to reach the last index.
      Idea: BFS by windows: [l, r] is everything reachable with `jumps`
      jumps; the farthest reach from it forms the next window.
      """,
      """
      def jump(nums):
          jumps = 0
          l = r = 0  # indexes reachable with `jumps` jumps
          while r < len(nums) - 1:
              farthest = 0
              for i in range(l, r + 1):
                  farthest = max(farthest, i + nums[i])
              l, r = r + 1, farthest
              jumps += 1
          return jumps
      """,
      "jump([2, 3, 1, 1, 4])",
      "2"),

    p(134, "Gas Station", "Medium",
      """
      Which station can you start at to drive the full circle?
      Idea: if the tank goes negative at i, no start between `start` and i
      works, so restart from i + 1.
      """,
      """
      def canCompleteCircuit(gas, cost):
          if sum(gas) < sum(cost):
              return -1
          tank = 0
          start = 0
          for i in range(len(gas)):
              tank += gas[i] - cost[i]
              if tank < 0:  # can't get past i from start
                  tank = 0
                  start = i + 1
          return start
      """,
      "canCompleteCircuit([1, 2, 3, 4, 5], [3, 4, 5, 1, 2])",
      "3"),

    p(846, "Hand of Straights", "Medium",
      """
      Can the cards be split into groups of consecutive values?
      Idea: the smallest remaining card must start a group. Use counts plus
      a min-heap of distinct values.
      """,
      """
      def isNStraightHand(hand, groupSize):
          if len(hand) % groupSize:
              return False
          count = Counter(hand)
          heap = list(count.keys())
          heapq.heapify(heap)
          while heap:
              first = heap[0]  # smallest card must start a group
              for card in range(first, first + groupSize):
                  if count[card] == 0:
                      return False
                  count[card] -= 1
                  if count[card] == 0:
                      if card != heap[0]:
                          return False
                      heapq.heappop(heap)
          return True
      """,
      "isNStraightHand([1, 2, 3, 6, 2, 3, 4, 7, 8], 3)",
      "True"),

    p(1899, "Merge Triplets to Form Target Triplet", "Medium",
      """
      Merging takes the max of each position. Can you build target?
      Idea: ignore triplets that exceed target anywhere; check the rest
      cover each target value exactly.
      """,
      """
      def mergeTriplets(triplets, target):
          good = set()  # target positions we can match exactly
          for t in triplets:
              if t[0] > target[0] or t[1] > target[1] or t[2] > target[2]:
                  continue  # would overshoot, never use it
              for i in range(3):
                  if t[i] == target[i]:
                      good.add(i)
          return len(good) == 3
      """,
      "mergeTriplets([[2, 5, 3], [1, 8, 4], [1, 7, 5]], [2, 7, 5])",
      "True"),

    p(763, "Partition Labels", "Medium",
      """
      Split s into as many parts as possible, each letter in only one part.
      Idea: record each letter's last index. A part must stretch to the last
      occurrence of everything inside it.
      """,
      """
      def partitionLabels(s):
          last = {ch: i for i, ch in enumerate(s)}
          res = []
          start = end = 0
          for i, ch in enumerate(s):
              end = max(end, last[ch])
              if i == end:
                  res.append(end - start + 1)
                  start = i + 1
          return res
      """,
      'partitionLabels("ababcbacadefegde")',
      "[9, 7]"),

    p(678, "Valid Parenthesis String", "Medium",
      """
      '*' can be '(', ')' or empty. Can the string be valid?
      Idea: track the range [left_min, left_max] of possible open counts.
      """,
      """
      def checkValidString(s):
          left_min, left_max = 0, 0  # range of possible open counts
          for ch in s:
              if ch == "(":
                  left_min, left_max = left_min + 1, left_max + 1
              elif ch == ")":
                  left_min, left_max = left_min - 1, left_max - 1
              else:  # "*" could be "(", ")" or empty
                  left_min, left_max = left_min - 1, left_max + 1
              if left_max < 0:
                  return False
              left_min = max(left_min, 0)
          return left_min == 0
      """,
      'checkValidString("(*))")',
      "True"),
]
