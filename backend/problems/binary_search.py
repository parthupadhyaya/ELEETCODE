from ._base import p

CATEGORY = "Binary Search"

PROBLEMS = [
    p(704, "Binary Search", "Easy",
      """
      Find target's index in a sorted array, or -1.
      Idea: compare with the middle and throw away the half that can't
      contain target. Halving each step gives O(log n).
      """,
      """
      def search(nums, target):
          l, r = 0, len(nums) - 1
          while l <= r:
              mid = (l + r) // 2
              if nums[mid] < target:
                  l = mid + 1
              elif nums[mid] > target:
                  r = mid - 1
              else:
                  return mid
          return -1
      """,
      "search([-1, 0, 3, 5, 9, 12], 9)",
      "4"),

    p(74, "Search a 2D Matrix", "Medium",
      """
      Each row is sorted and starts after the previous row ends. Find target.
      Idea: treat the matrix as one sorted array; index mid maps to
      (mid // cols, mid % cols).
      """,
      """
      def searchMatrix(matrix, target):
          rows, cols = len(matrix), len(matrix[0])
          l, r = 0, rows * cols - 1
          while l <= r:
              mid = (l + r) // 2
              row, col = divmod(mid, cols)
              val = matrix[row][col]
              if val < target:
                  l = mid + 1
              elif val > target:
                  r = mid - 1
              else:
                  return True
          return False
      """,
      "searchMatrix([[1, 3, 5, 7], [10, 11, 16, 20], [23, 30, 34, 60]], 16)",
      "True"),

    p(875, "Koko Eating Bananas", "Medium",
      """
      Minimum eating speed k so all piles are finished within h hours.
      Idea: binary search on the answer: if speed k works, every faster
      speed works too.
      """,
      """
      def minEatingSpeed(piles, h):
          lo, hi = 1, max(piles)
          best = hi
          while lo <= hi:
              speed = (lo + hi) // 2
              hours = 0
              for pile in piles:
                  hours += math.ceil(pile / speed)
              if hours <= h:
                  best = speed
                  hi = speed - 1
              else:
                  lo = speed + 1
          return best
      """,
      "minEatingSpeed([3, 6, 7, 11], 8)",
      "4"),

    p(153, "Find Minimum in Rotated Sorted Array", "Medium",
      """
      A sorted array was rotated. Find its minimum in O(log n).
      Idea: if nums[mid] > nums[r], the drop (minimum) is right of mid;
      otherwise it's at mid or to its left.
      """,
      """
      def findMin(nums):
          l, r = 0, len(nums) - 1
          while l < r:
              mid = (l + r) // 2
              if nums[mid] > nums[r]:
                  l = mid + 1
              else:
                  r = mid
          return nums[l]
      """,
      "findMin([4, 5, 6, 7, 0, 1, 2])",
      "0"),

    p(33, "Search in Rotated Sorted Array", "Medium",
      """
      Find target in a rotated sorted array in O(log n).
      Idea: one half around mid is always sorted. Check whether target lies
      in that sorted half; if not, search the other half.
      """,
      """
      def search(nums, target):
          l, r = 0, len(nums) - 1
          while l <= r:
              mid = (l + r) // 2
              if nums[mid] == target:
                  return mid
              if nums[l] <= nums[mid]:  # left half is sorted
                  if nums[l] <= target < nums[mid]:
                      r = mid - 1
                  else:
                      l = mid + 1
              else:  # right half is sorted
                  if nums[mid] < target <= nums[r]:
                      l = mid + 1
                  else:
                      r = mid - 1
          return -1
      """,
      "search([4, 5, 6, 7, 0, 1, 2], 0)",
      "4"),

    p(981, "Time Based Key-Value Store", "Medium",
      """
      set(key, value, time) and get(key, time) -> latest value at or before time.
      Idea: timestamps arrive increasing, so each key's list is sorted;
      binary search for the last timestamp <= time.
      """,
      """
      class TimeMap:
          def __init__(self):
              self.store = defaultdict(list)  # key -> [(timestamp, value)]

          def set(self, key, value, timestamp):
              self.store[key].append((timestamp, value))

          def get(self, key, timestamp):
              values = self.store[key]
              res = ""
              l, r = 0, len(values) - 1
              while l <= r:
                  mid = (l + r) // 2
                  if values[mid][0] <= timestamp:
                      res = values[mid][1]
                      l = mid + 1
                  else:
                      r = mid - 1
              return res
      """,
      """
      tm = TimeMap()
      tm.set("foo", "bar", 1)
      tm.set("foo", "bar2", 4)
      [tm.get("foo", 1), tm.get("foo", 3), tm.get("foo", 4), tm.get("foo", 5)]
      """,
      "['bar', 'bar', 'bar2', 'bar2']"),

    p(4, "Median of Two Sorted Arrays", "Hard",
      """
      Median of two sorted arrays in O(log(min(m, n))).
      Idea: binary search how many items the left half takes from the
      smaller array A; B supplies the rest. The split is right when every
      left item <= every right item.
      """,
      """
      def findMedianSortedArrays(nums1, nums2):
          A, B = nums1, nums2
          if len(A) > len(B):
              A, B = B, A
          total = len(A) + len(B)
          half = total // 2
          l, r = 0, len(A) - 1
          while True:
              i = (l + r) // 2  # last index taken from A
              j = half - i - 2  # last index taken from B
              a_left = A[i] if i >= 0 else float("-inf")
              a_right = A[i + 1] if i + 1 < len(A) else float("inf")
              b_left = B[j] if j >= 0 else float("-inf")
              b_right = B[j + 1] if j + 1 < len(B) else float("inf")
              if a_left <= b_right and b_left <= a_right:
                  if total % 2:
                      return min(a_right, b_right)
                  return (max(a_left, b_left) + min(a_right, b_right)) / 2
              elif a_left > b_right:
                  r = i - 1
              else:
                  l = i + 1
      """,
      "findMedianSortedArrays([1, 3, 8], [2, 4, 5, 9])",
      "4"),
]
