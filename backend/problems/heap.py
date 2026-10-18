from ._base import p

CATEGORY = "Heap / Priority Queue"

PROBLEMS = [
    p(703, "Kth Largest Element in a Stream", "Easy",
      """
      After each add, return the k-th largest value seen so far.
      Idea: keep a min-heap of only the k largest; its top is the answer.
      """,
      """
      class KthLargest:
          def __init__(self, k, nums):
              self.k = k
              self.heap = nums
              heapq.heapify(self.heap)
              while len(self.heap) > k:
                  heapq.heappop(self.heap)

          def add(self, val):
              heapq.heappush(self.heap, val)
              if len(self.heap) > self.k:
                  heapq.heappop(self.heap)
              return self.heap[0]
      """,
      """
      kl = KthLargest(3, [4, 5, 8, 2])
      [kl.add(3), kl.add(5), kl.add(10), kl.add(9), kl.add(4)]
      """,
      "[4, 5, 5, 8, 8]"),

    p(1046, "Last Stone Weight", "Easy",
      """
      Smash the two heaviest stones together until at most one is left.
      Idea: a max-heap (Python's heapq is a min-heap, so store negatives).
      """,
      """
      def lastStoneWeight(stones):
          heap = [-s for s in stones]  # max-heap via negatives
          heapq.heapify(heap)
          while len(heap) > 1:
              first = -heapq.heappop(heap)
              second = -heapq.heappop(heap)
              if first > second:
                  heapq.heappush(heap, -(first - second))
          return -heap[0] if heap else 0
      """,
      "lastStoneWeight([2, 7, 4, 1, 8, 1])",
      "1"),

    p(973, "K Closest Points to Origin", "Medium",
      """
      Return the k points closest to (0, 0).
      Idea: heap ordered by squared distance; pop k times.
      """,
      """
      def kClosest(points, k):
          heap = []
          for x, y in points:
              dist = x * x + y * y
              heapq.heappush(heap, (dist, x, y))
          res = []
          for _ in range(k):
              dist, x, y = heapq.heappop(heap)
              res.append([x, y])
          return res
      """,
      "kClosest([[3, 3], [5, -1], [-2, 4]], 2)",
      "[[3, 3], [-2, 4]]"),

    p(215, "Kth Largest Element in an Array", "Medium",
      """
      Return the k-th largest element.
      Idea: a min-heap of size k; anything smaller than its top is dropped.
      """,
      """
      def findKthLargest(nums, k):
          heap = []
          for n in nums:
              heapq.heappush(heap, n)
              if len(heap) > k:
                  heapq.heappop(heap)
          return heap[0]
      """,
      "findKthLargest([3, 2, 1, 5, 6, 4], 2)",
      "5"),

    p(621, "Task Scheduler", "Medium",
      """
      Same tasks need n idle slots between them. Minimum total time?
      Idea: always run the most frequent available task (max-heap). Cooling
      tasks wait in a queue with the time they become available again.
      """,
      """
      def leastInterval(tasks, n):
          count = Counter(tasks)
          heap = [-c for c in count.values()]
          heapq.heapify(heap)
          q = deque()  # (-remaining, time it can run again)
          time = 0
          while heap or q:
              time += 1
              if heap:
                  cnt = heapq.heappop(heap) + 1
                  if cnt:
                      q.append((cnt, time + n))
              if q and q[0][1] == time:
                  heapq.heappush(heap, q.popleft()[0])
          return time
      """,
      'leastInterval(["A", "A", "A", "B", "B", "B"], 2)',
      "8"),

    p(355, "Design Twitter", "Medium",
      """
      Post tweets, follow/unfollow, and get the 10 most recent tweets in a feed.
      Idea: per-user tweet lists with timestamps; merge followees' tweets
      with a heap ordered by newest first.
      """,
      """
      class Twitter:
          def __init__(self):
              self.time = 0
              self.tweets = defaultdict(list)  # user -> [(time, tweetId)]
              self.follows = defaultdict(set)

          def postTweet(self, userId, tweetId):
              self.tweets[userId].append((self.time, tweetId))
              self.time += 1

          def getNewsFeed(self, userId):
              heap = []
              for uid in self.follows[userId] | {userId}:
                  for t, tid in self.tweets[uid][-10:]:
                      heapq.heappush(heap, (-t, tid))
              res = []
              while heap and len(res) < 10:
                  res.append(heapq.heappop(heap)[1])
              return res

          def follow(self, followerId, followeeId):
              if followerId != followeeId:
                  self.follows[followerId].add(followeeId)

          def unfollow(self, followerId, followeeId):
              self.follows[followerId].discard(followeeId)
      """,
      """
      tw = Twitter()
      tw.postTweet(1, 5)
      feed1 = tw.getNewsFeed(1)
      tw.follow(1, 2)
      tw.postTweet(2, 6)
      feed2 = tw.getNewsFeed(1)
      tw.unfollow(1, 2)
      [feed1, feed2, tw.getNewsFeed(1)]
      """,
      "[[5], [6, 5], [5]]"),

    p(295, "Find Median from Data Stream", "Hard",
      """
      Add numbers one at a time and report the running median.
      Idea: a max-heap holds the smaller half, a min-heap the larger half.
      Keep them balanced; the median sits on top.
      """,
      """
      class MedianFinder:
          def __init__(self):
              self.small = []  # max-heap (negated): lower half
              self.large = []  # min-heap: upper half

          def addNum(self, num):
              heapq.heappush(self.small, -num)
              # move the biggest of the lower half up so small <= large
              heapq.heappush(self.large, -heapq.heappop(self.small))
              if len(self.large) > len(self.small):
                  heapq.heappush(self.small, -heapq.heappop(self.large))

          def findMedian(self):
              if len(self.small) > len(self.large):
                  return -self.small[0]
              return (-self.small[0] + self.large[0]) / 2
      """,
      """
      mf = MedianFinder()
      mf.addNum(1)
      mf.addNum(2)
      out = [mf.findMedian()]
      mf.addNum(3)
      out.append(mf.findMedian())
      out
      """,
      "[1.5, 2]"),
]
