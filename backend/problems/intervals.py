from ._base import p

CATEGORY = "Intervals"

PROBLEMS = [
    p(57, "Insert Interval", "Medium",
      """
      Insert newInterval into sorted, non-overlapping intervals.
      Idea: copy intervals that end before it, merge the ones that overlap,
      then append the rest.
      """,
      """
      def insert(intervals, newInterval):
          res = []
          for i, (start, end) in enumerate(intervals):
              if newInterval[1] < start:  # new one ends before this starts
                  res.append(newInterval)
                  return res + intervals[i:]
              if newInterval[0] > end:  # new one starts after this ends
                  res.append([start, end])
              else:  # overlap: grow newInterval to cover both
                  newInterval = [min(newInterval[0], start), max(newInterval[1], end)]
          res.append(newInterval)
          return res
      """,
      "insert([[1, 2], [3, 5], [6, 7], [8, 10], [12, 16]], [4, 8])",
      "[[1, 2], [3, 10], [12, 16]]"),

    p(56, "Merge Intervals", "Medium",
      """
      Merge all overlapping intervals.
      Idea: sort by start; each interval either extends the last merged one
      or starts a new one.
      """,
      """
      def merge(intervals):
          intervals.sort(key=lambda iv: iv[0])
          merged = [intervals[0]]
          for start, end in intervals[1:]:
              last_end = merged[-1][1]
              if start <= last_end:
                  merged[-1][1] = max(last_end, end)
              else:
                  merged.append([start, end])
          return merged
      """,
      "merge([[1, 3], [8, 10], [2, 6], [15, 18]])",
      "[[1, 6], [8, 10], [15, 18]]"),

    p(435, "Non-overlapping Intervals", "Medium",
      """
      Fewest intervals to remove so the rest don't overlap.
      Idea: sort by end and keep greedily: the interval that ends first
      leaves the most room for the others.
      """,
      """
      def eraseOverlapIntervals(intervals):
          intervals.sort(key=lambda iv: iv[1])
          removed = 0
          prev_end = float("-inf")
          for start, end in intervals:
              if start >= prev_end:
                  prev_end = end  # keep it: it ends earliest
              else:
                  removed += 1
          return removed
      """,
      "eraseOverlapIntervals([[1, 2], [2, 3], [3, 4], [1, 3]])",
      "1"),

    p(252, "Meeting Rooms", "Easy",
      """
      Can one person attend every meeting?
      Idea: sort by start; any meeting starting before the previous one
      ends is a conflict.
      """,
      """
      def canAttendMeetings(intervals):
          intervals.sort()
          for i in range(1, len(intervals)):
              if intervals[i][0] < intervals[i - 1][1]:
                  return False
          return True
      """,
      "canAttendMeetings([[0, 30], [5, 10], [15, 20]])",
      "False"),

    p(253, "Meeting Rooms II", "Medium",
      """
      Minimum number of rooms needed.
      Idea: sort start and end times separately and sweep: a start before
      the earliest end needs another room; otherwise a room frees up.
      """,
      """
      def minMeetingRooms(intervals):
          starts = sorted(iv[0] for iv in intervals)
          ends = sorted(iv[1] for iv in intervals)
          rooms = best = 0
          s = e = 0
          while s < len(starts):
              if starts[s] < ends[e]:
                  rooms += 1  # a meeting starts before the earliest end
                  s += 1
              else:
                  rooms -= 1  # a meeting ended, its room is free
                  e += 1
              best = max(best, rooms)
          return best
      """,
      "minMeetingRooms([[0, 30], [5, 10], [15, 20]])",
      "2"),

    p(1851, "Minimum Interval to Include Each Query", "Hard",
      """
      For each query, the size of the smallest interval containing it.
      Idea: process queries in sorted order. Push intervals that have
      started into a heap by size, pop ones that already ended.
      """,
      """
      def minInterval(intervals, queries):
          intervals.sort()
          heap = []  # (size, right end) of intervals that have started
          res = {}
          i = 0
          for q in sorted(queries):
              while i < len(intervals) and intervals[i][0] <= q:
                  l, r = intervals[i]
                  heapq.heappush(heap, (r - l + 1, r))
                  i += 1
              while heap and heap[0][1] < q:
                  heapq.heappop(heap)  # ended before q
              res[q] = heap[0][0] if heap else -1
          return [res[q] for q in queries]
      """,
      "minInterval([[1, 4], [2, 4], [3, 6], [4, 4]], [2, 3, 4, 5])",
      "[3, 3, 1, 4]"),
]
