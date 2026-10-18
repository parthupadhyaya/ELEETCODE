from ._base import p

CATEGORY = "Bit Manipulation"

PROBLEMS = [
    p(136, "Single Number", "Easy",
      """
      Every number appears twice except one. Find it with O(1) memory.
      Idea: XOR everything; a ^ a = 0, so pairs cancel and the single remains.
      """,
      """
      def singleNumber(nums):
          res = 0
          for n in nums:
              res ^= n  # pairs cancel out: a ^ a = 0
          return res
      """,
      "singleNumber([4, 1, 2, 1, 2])",
      "4"),

    p(191, "Number of 1 Bits", "Easy",
      """
      Count the 1 bits in n.
      Idea: n & (n - 1) clears the lowest 1 bit; count how many times
      until n is 0.
      """,
      """
      def hammingWeight(n):
          count = 0
          while n:
              n &= n - 1  # clears the lowest set bit
              count += 1
          return count
      """,
      "hammingWeight(11)",
      "3"),

    p(338, "Counting Bits", "Easy",
      """
      For every i in 0..n, count its 1 bits.
      Idea: i >> 1 is i without its last bit, already computed:
      dp[i] = dp[i >> 1] + (i & 1).
      """,
      """
      def countBits(n):
          dp = [0] * (n + 1)
          for i in range(1, n + 1):
              dp[i] = dp[i >> 1] + (i & 1)  # bits of i // 2, plus the last bit
          return dp
      """,
      "countBits(5)",
      "[0, 1, 1, 2, 1, 2]"),

    p(190, "Reverse Bits", "Easy",
      """
      Reverse the 32 bits of n.
      Idea: read bit i from the right and write it at position 31 - i.
      """,
      """
      def reverseBits(n):
          res = 0
          for i in range(32):
              bit = (n >> i) & 1
              res |= bit << (31 - i)
          return res
      """,
      "reverseBits(43261596)",
      "964176192"),

    p(268, "Missing Number", "Easy",
      """
      nums holds n distinct numbers from 0..n. Which one is missing?
      Idea: XOR every index and every value; everything pairs up except
      the missing number.
      """,
      """
      def missingNumber(nums):
          res = len(nums)
          for i, n in enumerate(nums):
              res ^= i ^ n
          return res
      """,
      "missingNumber([3, 0, 1])",
      "2"),

    p(371, "Sum of Two Integers", "Medium",
      """
      Add a and b without using + or -.
      Idea: a ^ b adds without carrying; (a & b) << 1 is the carry. Repeat
      until there's no carry. The mask emulates 32-bit integers.
      """,
      """
      def getSum(a, b):
          mask = 0xFFFFFFFF  # emulate 32-bit integers
          while (b & mask) > 0:
              carry = (a & b) << 1
              a = a ^ b  # add without carrying
              b = carry
          return (a & mask) if b > 0 else a
      """,
      "getSum(9, 11)",
      "20"),

    p(7, "Reverse Integer", "Medium",
      """
      Reverse the digits of a 32-bit integer (0 if it overflows).
      Idea: pop the last digit with divmod and push it onto the result.
      """,
      """
      def reverse(x):
          sign = -1 if x < 0 else 1
          x = abs(x)
          res = 0
          while x:
              x, digit = divmod(x, 10)
              res = res * 10 + digit
          res *= sign
          return res if -2**31 <= res <= 2**31 - 1 else 0
      """,
      "reverse(-123)",
      "-321"),
]
