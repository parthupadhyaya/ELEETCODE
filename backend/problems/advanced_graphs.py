from ._base import p

CATEGORY = "Advanced Graphs"

PROBLEMS = [
    p(743, "Network Delay Time", "Medium",
      """
      How long until a signal from k reaches every node (-1 if some can't)?
      Idea: Dijkstra. A min-heap always expands the closest unfinished node;
      its first pop is its shortest distance.
      """,
      """
      def networkDelayTime(times, n, k):
          graph = defaultdict(list)
          for u, v, w in times:
              graph[u].append((v, w))
          dist = {}
          heap = [(0, k)]
          while heap:
              d, node = heapq.heappop(heap)
              if node in dist:
                  continue
              dist[node] = d
              for nei, w in graph[node]:
                  if nei not in dist:
                      heapq.heappush(heap, (d + w, nei))
          return max(dist.values()) if len(dist) == n else -1
      """,
      "networkDelayTime([[2, 1, 1], [2, 3, 1], [3, 4, 1]], 4, 2)",
      "2"),

    p(332, "Reconstruct Itinerary", "Hard",
      """
      Use every ticket once, starting at JFK, smallest lexical order.
      Idea: Hierholzer's algorithm: follow the smallest unused ticket; when
      stuck, add the airport to the route. The reversed route is the answer.
      """,
      """
      def findItinerary(tickets):
          graph = defaultdict(list)
          for src, dst in sorted(tickets, reverse=True):
              graph[src].append(dst)  # reversed, so pop() gives the smallest
          route = []

          def visit(airport):
              while graph[airport]:
                  visit(graph[airport].pop())
              route.append(airport)

          visit("JFK")
          return route[::-1]
      """,
      'findItinerary([["MUC", "LHR"], ["JFK", "MUC"], ["SFO", "SJC"], ["LHR", "SFO"]])',
      "['JFK', 'MUC', 'LHR', 'SFO', 'SJC']"),

    p(1584, "Min Cost to Connect All Points", "Medium",
      """
      Cheapest way to connect every point (Manhattan distance edges).
      Idea: Prim's minimum spanning tree: grow the tree by always adding the
      cheapest edge to a new point (min-heap).
      """,
      """
      def minCostConnectPoints(points):
          n = len(points)
          in_tree = set()
          heap = [(0, 0)]  # (cost to connect, point index)
          total = 0
          while len(in_tree) < n:
              cost, i = heapq.heappop(heap)
              if i in in_tree:
                  continue
              in_tree.add(i)
              total += cost
              xi, yi = points[i]
              for j in range(n):
                  if j not in in_tree:
                      xj, yj = points[j]
                      heapq.heappush(heap, (abs(xi - xj) + abs(yi - yj), j))
          return total
      """,
      "minCostConnectPoints([[0, 0], [2, 2], [3, 10], [5, 2], [7, 0]])",
      "20"),

    p(778, "Swim in Rising Water", "Hard",
      """
      At time t you can swim through cells with height <= t. Earliest time
      to reach the bottom-right?
      Idea: Dijkstra where a path's cost is its tallest cell.
      """,
      """
      def swimInWater(grid):
          n = len(grid)
          seen = {(0, 0)}
          heap = [(grid[0][0], 0, 0)]  # (tallest cell on path, r, c)
          while heap:
              t, r, c = heapq.heappop(heap)
              if r == c == n - 1:
                  return t
              for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                  if 0 <= nr < n and 0 <= nc < n and (nr, nc) not in seen:
                      seen.add((nr, nc))
                      heapq.heappush(heap, (max(t, grid[nr][nc]), nr, nc))
      """,
      "swimInWater([[0, 1, 2, 3], [11, 10, 9, 4], [12, 13, 14, 5], [8, 7, 6, 15]])",
      "15"),

    p(269, "Alien Dictionary", "Hard",
      """
      Words are sorted in an alien alphabet; recover the letter order.
      Idea: the first differing letter of adjacent words gives an edge
      a -> b. Topologically sort with DFS (a cycle means no valid order).
      """,
      """
      def alienOrder(words):
          graph = {ch: set() for w in words for ch in w}
          for w1, w2 in zip(words, words[1:]):
              min_len = min(len(w1), len(w2))
              if len(w1) > len(w2) and w1[:min_len] == w2[:min_len]:
                  return ""  # a longer word can't come before its prefix
              for a, b in zip(w1, w2):
                  if a != b:
                      graph[a].add(b)  # a comes before b
                      break
          state = {}  # False = on current path, True = finished
          order = []

          def dfs(ch):  # True means a cycle was found
              if ch in state:
                  return not state[ch]
              state[ch] = False
              for nxt in graph[ch]:
                  if dfs(nxt):
                      return True
              state[ch] = True
              order.append(ch)
              return False

          for ch in graph:
              if dfs(ch):
                  return ""
          return "".join(reversed(order))
      """,
      'alienOrder(["wrt", "wrf", "er", "ett", "rftt"])',
      "'wertf'"),

    p(787, "Cheapest Flights Within K Stops", "Medium",
      """
      Cheapest price from src to dst using at most k stops.
      Idea: Bellman-Ford limited to k + 1 rounds. Each round relaxes every
      flight once, using a copy so a round adds at most one more flight.
      """,
      """
      def findCheapestPrice(n, flights, src, dst, k):
          prices = [float("inf")] * n
          prices[src] = 0
          for _ in range(k + 1):
              tmp = prices.copy()
              for s, d, cost in flights:
                  if prices[s] != float("inf") and prices[s] + cost < tmp[d]:
                      tmp[d] = prices[s] + cost
              prices = tmp
          return -1 if prices[dst] == float("inf") else prices[dst]
      """,
      "findCheapestPrice(4, [[0, 1, 100], [1, 2, 100], [2, 0, 100], [1, 3, 600], [2, 3, 200]], 0, 3, 1)",
      "700"),
]
