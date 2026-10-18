from ._base import p

CATEGORY = "Graphs"

PROBLEMS = [
    p(200, "Number of Islands", "Medium",
      """
      Count groups of connected "1" cells (up/down/left/right).
      Idea: scan the grid; each unseen land cell starts a new island, and a
      DFS marks the whole island as seen.
      """,
      """
      def numIslands(grid):
          rows, cols = len(grid), len(grid[0])
          seen = set()

          def dfs(r, c):
              if (r, c) in seen or not (0 <= r < rows and 0 <= c < cols):
                  return
              if grid[r][c] == "0":
                  return
              seen.add((r, c))
              for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                  dfs(r + dr, c + dc)

          count = 0
          for r in range(rows):
              for c in range(cols):
                  if grid[r][c] == "1" and (r, c) not in seen:
                      dfs(r, c)
                      count += 1
          return count
      """,
      """
      numIslands([
          ["1", "1", "0", "0", "0"],
          ["1", "1", "0", "0", "0"],
          ["0", "0", "1", "0", "0"],
          ["0", "0", "0", "1", "1"],
      ])
      """,
      "3"),

    p(695, "Max Area of Island", "Medium",
      """
      Size of the largest island.
      Idea: DFS returns 1 + the area of its four neighbours.
      """,
      """
      def maxAreaOfIsland(grid):
          rows, cols = len(grid), len(grid[0])
          seen = set()

          def area(r, c):
              if (r < 0 or c < 0 or r >= rows or c >= cols
                      or grid[r][c] == 0 or (r, c) in seen):
                  return 0
              seen.add((r, c))
              return 1 + area(r + 1, c) + area(r - 1, c) + area(r, c + 1) + area(r, c - 1)

          best = 0
          for r in range(rows):
              for c in range(cols):
                  best = max(best, area(r, c))
          return best
      """,
      "maxAreaOfIsland([[0, 1, 1, 0], [0, 1, 1, 0], [1, 0, 0, 1], [1, 1, 0, 1]])",
      "4"),

    p(133, "Clone Graph", "Medium",
      """
      Deep-copy a connected undirected graph.
      Idea: DFS with a hashmap old -> copy. Seeing a node again returns its
      existing copy, which also stops infinite loops on cycles.
      """,
      """
      class Node:
          def __init__(self, val=0, neighbors=None):
              self.val = val
              self.neighbors = neighbors if neighbors is not None else []

      def cloneGraph(node):
          old_to_new = {}

          def clone(node):
              if node in old_to_new:
                  return old_to_new[node]
              copy = Node(node.val)
              old_to_new[node] = copy
              for nei in node.neighbors:
                  copy.neighbors.append(clone(nei))
              return copy

          return clone(node) if node else None
      """,
      """
      n1, n2, n3, n4 = Node(1), Node(2), Node(3), Node(4)
      n1.neighbors = [n2, n4]
      n2.neighbors = [n1, n3]
      n3.neighbors = [n2, n4]
      n4.neighbors = [n1, n3]
      copy = cloneGraph(n1)
      [[nei.val for nei in n.neighbors] for n in [copy, copy.neighbors[0], copy.neighbors[0].neighbors[1], copy.neighbors[1]]]
      """,
      "[[2, 4], [1, 3], [2, 4], [1, 3]]"),

    p(286, "Walls and Gates", "Medium",
      """
      Fill each empty room (INF) with the distance to its nearest gate (0).
      Walls are -1.
      Idea: multi-source BFS: start from every gate at once, so the first
      time a room is reached is its shortest distance.
      """,
      """
      def wallsAndGates(rooms):
          INF = 2147483647
          rows, cols = len(rooms), len(rooms[0])
          q = deque()
          for r in range(rows):
              for c in range(cols):
                  if rooms[r][c] == 0:
                      q.append((r, c))
          while q:
              r, c = q.popleft()
              for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                  if 0 <= nr < rows and 0 <= nc < cols and rooms[nr][nc] == INF:
                      rooms[nr][nc] = rooms[r][c] + 1
                      q.append((nr, nc))
          return rooms
      """,
      """
      INF = 2147483647
      wallsAndGates([
          [INF, -1, 0, INF],
          [INF, INF, INF, -1],
          [INF, -1, INF, -1],
          [0, -1, INF, INF],
      ])
      """,
      "[[3, -1, 0, 1], [2, 2, 1, -1], [1, -1, 2, -1], [0, -1, 3, 4]]"),

    p(994, "Rotting Oranges", "Medium",
      """
      Each minute, rotten oranges (2) rot their fresh neighbours (1).
      How many minutes until none are fresh (-1 if impossible)?
      Idea: BFS level by level from every rotten orange; one level = one minute.
      """,
      """
      def orangesRotting(grid):
          rows, cols = len(grid), len(grid[0])
          q = deque()
          fresh = 0
          for r in range(rows):
              for c in range(cols):
                  if grid[r][c] == 2:
                      q.append((r, c))
                  elif grid[r][c] == 1:
                      fresh += 1
          minutes = 0
          while q and fresh:
              for _ in range(len(q)):
                  r, c = q.popleft()
                  for nr, nc in ((r + 1, c), (r - 1, c), (r, c + 1), (r, c - 1)):
                      if 0 <= nr < rows and 0 <= nc < cols and grid[nr][nc] == 1:
                          grid[nr][nc] = 2
                          fresh -= 1
                          q.append((nr, nc))
              minutes += 1
          return minutes if fresh == 0 else -1
      """,
      "orangesRotting([[2, 1, 1], [1, 1, 0], [0, 1, 1]])",
      "4"),

    p(417, "Pacific Atlantic Water Flow", "Medium",
      """
      Which cells can drain to both the Pacific (top/left) and the Atlantic
      (bottom/right)? Water flows to equal or lower neighbours.
      Idea: search uphill from each ocean's edge; answer = cells in both sets.
      """,
      """
      def pacificAtlantic(heights):
          rows, cols = len(heights), len(heights[0])
          pac, atl = set(), set()

          def dfs(r, c, visit, prev_height):
              if ((r, c) in visit or r < 0 or c < 0 or r >= rows or c >= cols
                      or heights[r][c] < prev_height):
                  return
              visit.add((r, c))
              for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                  dfs(r + dr, c + dc, visit, heights[r][c])

          for c in range(cols):
              dfs(0, c, pac, heights[0][c])
              dfs(rows - 1, c, atl, heights[rows - 1][c])
          for r in range(rows):
              dfs(r, 0, pac, heights[r][0])
              dfs(r, cols - 1, atl, heights[r][cols - 1])
          return sorted([r, c] for r, c in pac & atl)
      """,
      "pacificAtlantic([[1, 2, 3], [8, 9, 4], [7, 6, 5]])",
      "[[0, 2], [1, 0], [1, 1], [1, 2], [2, 0], [2, 1], [2, 2]]"),

    p(130, "Surrounded Regions", "Medium",
      """
      Flip every "O" region that doesn't touch the border into "X".
      Idea: reverse the question: mark border-connected O's as safe ("T"),
      flip everything else, then restore the safe ones.
      """,
      """
      def solve(board):
          rows, cols = len(board), len(board[0])

          def capture(r, c):  # mark border-connected O's as safe
              if r < 0 or c < 0 or r >= rows or c >= cols or board[r][c] != "O":
                  return
              board[r][c] = "T"
              capture(r + 1, c)
              capture(r - 1, c)
              capture(r, c + 1)
              capture(r, c - 1)

          for r in range(rows):
              for c in range(cols):
                  if board[r][c] == "O" and (r in (0, rows - 1) or c in (0, cols - 1)):
                      capture(r, c)
          for r in range(rows):
              for c in range(cols):
                  if board[r][c] == "O":
                      board[r][c] = "X"
                  elif board[r][c] == "T":
                      board[r][c] = "O"
          return board
      """,
      'solve([["X", "X", "X", "X"], ["X", "O", "O", "X"], ["X", "X", "O", "X"], ["X", "O", "X", "X"]])',
      "[['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'X', 'X', 'X'], ['X', 'O', 'X', 'X']]"),

    p(207, "Course Schedule", "Medium",
      """
      Can every course be finished given the prerequisite pairs?
      Idea: build a graph course -> prerequisites and look for a cycle with
      DFS. `visiting` is the current path; reaching it again means a cycle.
      """,
      """
      def canFinish(numCourses, prerequisites):
          graph = {c: [] for c in range(numCourses)}
          for course, pre in prerequisites:
              graph[course].append(pre)
          visiting = set()  # courses on the current DFS path
          done = set()

          def dfs(c):
              if c in visiting:
                  return False  # cycle!
              if c in done:
                  return True
              visiting.add(c)
              for pre in graph[c]:
                  if not dfs(pre):
                      return False
              visiting.remove(c)
              done.add(c)
              return True

          for c in range(numCourses):
              if not dfs(c):
                  return False
          return True
      """,
      "canFinish(4, [[1, 0], [2, 1], [3, 1], [3, 2]])",
      "True"),

    p(210, "Course Schedule II", "Medium",
      """
      Return an order to take all courses (or [] if impossible).
      Idea: Kahn's topological sort: repeatedly take a course with no
      remaining prerequisites (indegree 0).
      """,
      """
      def findOrder(numCourses, prerequisites):
          graph = {c: [] for c in range(numCourses)}
          indegree = [0] * numCourses
          for course, pre in prerequisites:
              graph[pre].append(course)
              indegree[course] += 1
          q = deque(c for c in range(numCourses) if indegree[c] == 0)
          order = []
          while q:
              c = q.popleft()
              order.append(c)
              for nxt in graph[c]:
                  indegree[nxt] -= 1
                  if indegree[nxt] == 0:
                      q.append(nxt)
          return order if len(order) == numCourses else []
      """,
      "findOrder(4, [[1, 0], [2, 0], [3, 1], [3, 2]])",
      "[0, 1, 2, 3]"),

    p(261, "Graph Valid Tree", "Medium",
      """
      Do these n nodes and edges form a tree?
      Idea: a tree has exactly n - 1 edges and is connected. DFS from 0
      (ignoring the edge back to the parent) and check every node is seen.
      """,
      """
      def validTree(n, edges):
          if len(edges) != n - 1:
              return False
          graph = {i: [] for i in range(n)}
          for a, b in edges:
              graph[a].append(b)
              graph[b].append(a)
          seen = set()

          def dfs(node, parent):
              if node in seen:
                  return False
              seen.add(node)
              for nei in graph[node]:
                  if nei != parent and not dfs(nei, node):
                      return False
              return True

          return dfs(0, -1) and len(seen) == n
      """,
      "validTree(5, [[0, 1], [0, 2], [0, 3], [1, 4]])",
      "True"),

    p(323, "Number of Connected Components in an Undirected Graph", "Medium",
      """
      Count connected components.
      Idea: union-find. Start with n components; every union of two
      different roots merges two components into one.
      """,
      """
      def countComponents(n, edges):
          parent = list(range(n))
          rank = [1] * n

          def find(x):
              while parent[x] != x:
                  parent[x] = parent[parent[x]]  # path compression
                  x = parent[x]
              return x

          def union(a, b):
              ra, rb = find(a), find(b)
              if ra == rb:
                  return 0
              if rank[ra] < rank[rb]:
                  ra, rb = rb, ra
              parent[rb] = ra
              rank[ra] += rank[rb]
              return 1

          components = n
          for a, b in edges:
              components -= union(a, b)
          return components
      """,
      "countComponents(5, [[0, 1], [1, 2], [3, 4]])",
      "2"),

    p(684, "Redundant Connection", "Medium",
      """
      A tree had one extra edge added. Find that edge.
      Idea: union-find; the first edge whose ends already share a root
      would close a cycle.
      """,
      """
      def findRedundantConnection(edges):
          parent = list(range(len(edges) + 1))

          def find(x):
              while parent[x] != x:
                  parent[x] = parent[parent[x]]
                  x = parent[x]
              return x

          for a, b in edges:
              ra, rb = find(a), find(b)
              if ra == rb:
                  return [a, b]
              parent[rb] = ra
          return []
      """,
      "findRedundantConnection([[1, 2], [1, 3], [2, 3]])",
      "[2, 3]"),

    p(127, "Word Ladder", "Hard",
      """
      Fewest one-letter changes from beginWord to endWord using wordList.
      Idea: BFS. Words sharing a wildcard pattern ("h*t") are neighbours,
      so a pattern -> words hashmap finds neighbours quickly.
      """,
      """
      def ladderLength(beginWord, endWord, wordList):
          if endWord not in wordList:
              return 0
          patterns = defaultdict(list)  # "h*t" -> words matching it
          for word in wordList + [beginWord]:
              for i in range(len(word)):
                  patterns[word[:i] + "*" + word[i + 1:]].append(word)
          seen = {beginWord}
          q = deque([beginWord])
          length = 1
          while q:
              for _ in range(len(q)):
                  word = q.popleft()
                  if word == endWord:
                      return length
                  for i in range(len(word)):
                      for nei in patterns[word[:i] + "*" + word[i + 1:]]:
                          if nei not in seen:
                              seen.add(nei)
                              q.append(nei)
              length += 1
          return 0
      """,
      'ladderLength("hit", "cog", ["hot", "dot", "dog", "lot", "log", "cog"])',
      "5"),
]
