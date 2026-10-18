from ._base import p

CATEGORY = "Two Pointers"

PROBLEMS = [
    p(125, "Valid Palindrome", "Easy",
      """
      Ignoring case and non-alphanumeric characters, is s a palindrome?
      Idea: pointers l and r walk inward, skipping junk and comparing.
      """,
      """
      def isPalindrome(s):
          l, r = 0, len(s) - 1
          while l < r:
              while l < r and not s[l].isalnum():
                  l += 1
              while l < r and not s[r].isalnum():
                  r -= 1
              if s[l].lower() != s[r].lower():
                  return False
              l += 1
              r -= 1
          return True
      """,
      'isPalindrome("No lemon, no melon")',
      "True"),

    p(167, "Two Sum II - Input Array Is Sorted", "Medium",
      """
      numbers is sorted; return 1-based indexes of two numbers summing to target.
      Idea: sum too big -> move r left; too small -> move l right.
      """,
      """
      def twoSum(numbers, target):
          l, r = 0, len(numbers) - 1
          while l < r:
              total = numbers[l] + numbers[r]
              if total > target:
                  r -= 1
              elif total < target:
                  l += 1
              else:
                  return [l + 1, r + 1]
      """,
      "twoSum([1, 3, 4, 5, 7, 10, 11], 9)",
      "[3, 4]"),

    p(15, "3Sum", "Medium",
      """
      Find all unique triplets that sum to 0.
      Idea: sort, fix nums[i], then run Two Sum II with l and r on the rest.
      Skip equal neighbours to avoid duplicate triplets.
      """,
      """
      def threeSum(nums):
          nums.sort()
          res = []
          for i in range(len(nums)):
              if i > 0 and nums[i] == nums[i - 1]:
                  continue
              l, r = i + 1, len(nums) - 1
              while l < r:
                  total = nums[i] + nums[l] + nums[r]
                  if total > 0:
                      r -= 1
                  elif total < 0:
                      l += 1
                  else:
                      res.append([nums[i], nums[l], nums[r]])
                      l += 1
                      r -= 1
                      while l < r and nums[l] == nums[l - 1]:
                          l += 1
          return res
      """,
      "threeSum([-1, 0, 1, 2, -1, -4])",
      "[[-1, -1, 2], [-1, 0, 1]]"),

    p(11, "Container With Most Water", "Medium",
      """
      Pick two lines that hold the most water: (r - l) * min(height).
      Idea: start wide; always move the shorter line, since the taller one
      can't help while the short one limits the height.
      """,
      """
      def maxArea(height):
          l, r = 0, len(height) - 1
          best = 0
          while l < r:
              area = (r - l) * min(height[l], height[r])
              best = max(best, area)
              if height[l] < height[r]:
                  l += 1
              else:
                  r -= 1
          return best
      """,
      "maxArea([1, 8, 6, 2, 5, 4, 8, 3, 7])",
      "49"),

    p(42, "Trapping Rain Water", "Hard",
      """
      How much rain water is trapped between the bars?
      Idea: water above a bar = min(max left, max right) - bar. Move the side
      with the smaller max inward; that side's max is the limiting wall.
      """,
      """
      def trap(height):
          l, r = 0, len(height) - 1
          left_max, right_max = height[l], height[r]
          water = 0
          while l < r:
              if left_max < right_max:
                  l += 1
                  left_max = max(left_max, height[l])
                  water += left_max - height[l]
              else:
                  r -= 1
                  right_max = max(right_max, height[r])
                  water += right_max - height[r]
          return water
      """,
      "trap([0, 1, 0, 2, 1, 0, 1, 3, 2, 1, 2, 1])",
      "6"),
]
