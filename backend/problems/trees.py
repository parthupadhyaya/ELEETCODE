from ._base import p

CATEGORY = "Trees"

PROBLEMS = [
    p(226, "Invert Binary Tree", "Easy",
      """
      Mirror the tree: swap every node's left and right children.
      Idea: swap at this node, then recurse into both children.
      """,
      """
      def invertTree(root):
          if not root:
              return None
          root.left, root.right = root.right, root.left
          invertTree(root.left)
          invertTree(root.right)
          return root
      """,
      "invertTree(build_tree([4, 2, 7, 1, 3, 6, 9]))",
      "[4, 7, 2, 9, 6, 3, 1]"),

    p(104, "Maximum Depth of Binary Tree", "Easy",
      """
      Number of nodes on the longest root-to-leaf path.
      Idea: depth = 1 + the deeper of the two subtrees (empty tree = 0).
      """,
      """
      def maxDepth(root):
          if not root:
              return 0
          return 1 + max(maxDepth(root.left), maxDepth(root.right))
      """,
      "maxDepth(build_tree([3, 9, 20, None, None, 15, 7]))",
      "3"),

    p(543, "Diameter of Binary Tree", "Easy",
      """
      Longest path (in edges) between any two nodes.
      Idea: the longest path through a node is height(left) + height(right).
      Compute heights bottom-up and track the best sum.
      """,
      """
      def diameterOfBinaryTree(root):
          best = 0

          def height(node):
              nonlocal best
              if not node:
                  return 0
              left = height(node.left)
              right = height(node.right)
              best = max(best, left + right)
              return 1 + max(left, right)

          height(root)
          return best
      """,
      "diameterOfBinaryTree(build_tree([1, 2, 3, 4, 5]))",
      "3"),

    p(110, "Balanced Binary Tree", "Easy",
      """
      Is every node's left/right height difference at most 1?
      Idea: return the height bottom-up, or -1 as soon as a subtree is
      unbalanced so the whole answer short-circuits.
      """,
      """
      def isBalanced(root):
          def check(node):  # height, or -1 if unbalanced
              if not node:
                  return 0
              left = check(node.left)
              right = check(node.right)
              if left == -1 or right == -1 or abs(left - right) > 1:
                  return -1
              return 1 + max(left, right)

          return check(root) != -1
      """,
      "isBalanced(build_tree([3, 9, 20, None, None, 15, 7]))",
      "True"),

    p(100, "Same Tree", "Easy",
      """
      Are two trees identical in shape and values?
      Idea: compare roots, then recursively compare left and right.
      """,
      """
      def isSameTree(p, q):
          if not p and not q:
              return True
          if not p or not q or p.val != q.val:
              return False
          return isSameTree(p.left, q.left) and isSameTree(p.right, q.right)
      """,
      "isSameTree(build_tree([1, 2, 3]), build_tree([1, 2, 3]))",
      "True"),

    p(572, "Subtree of Another Tree", "Easy",
      """
      Does root contain a subtree identical to subRoot?
      Idea: at each node of root, run Same Tree against subRoot.
      """,
      """
      def isSubtree(root, subRoot):
          if not subRoot:
              return True
          if not root:
              return False
          if sameTree(root, subRoot):
              return True
          return isSubtree(root.left, subRoot) or isSubtree(root.right, subRoot)

      def sameTree(a, b):
          if not a and not b:
              return True
          if not a or not b or a.val != b.val:
              return False
          return sameTree(a.left, b.left) and sameTree(a.right, b.right)
      """,
      "isSubtree(build_tree([3, 4, 5, 1, 2]), build_tree([4, 1, 2]))",
      "True"),

    p(235, "Lowest Common Ancestor of a BST", "Medium",
      """
      Deepest node that has both p and q as descendants.
      Idea: in a BST, if both are bigger go right, both smaller go left;
      otherwise this node is where they split.
      """,
      """
      def lowestCommonAncestor(root, p, q):
          curr = root
          while curr:
              if p.val > curr.val and q.val > curr.val:
                  curr = curr.right
              elif p.val < curr.val and q.val < curr.val:
                  curr = curr.left
              else:
                  return curr
      """,
      """
      root = build_tree([6, 2, 8, 0, 4, 7, 9, None, None, 3, 5])
      lowestCommonAncestor(root, find_node(root, 3), find_node(root, 5)).val
      """,
      "4"),

    p(102, "Binary Tree Level Order Traversal", "Medium",
      """
      Values level by level, left to right.
      Idea: BFS with a queue; process exactly len(q) nodes per level.
      """,
      """
      def levelOrder(root):
          res = []
          q = deque([root] if root else [])
          while q:
              level = []
              for _ in range(len(q)):
                  node = q.popleft()
                  level.append(node.val)
                  if node.left:
                      q.append(node.left)
                  if node.right:
                      q.append(node.right)
              res.append(level)
          return res
      """,
      "levelOrder(build_tree([3, 9, 20, None, None, 15, 7]))",
      "[[3], [9, 20], [15, 7]]"),

    p(199, "Binary Tree Right Side View", "Medium",
      """
      Values visible when looking at the tree from the right.
      Idea: BFS by level; the last node in each level is visible.
      """,
      """
      def rightSideView(root):
          res = []
          q = deque([root] if root else [])
          while q:
              res.append(q[-1].val)
              for _ in range(len(q)):
                  node = q.popleft()
                  if node.left:
                      q.append(node.left)
                  if node.right:
                      q.append(node.right)
          return res
      """,
      "rightSideView(build_tree([1, 2, 3, None, 5, None, 4]))",
      "[1, 3, 4]"),

    p(1448, "Count Good Nodes in Binary Tree", "Medium",
      """
      A node is good if nothing on the path from the root is bigger than it.
      Idea: DFS carrying the max value seen on the path so far.
      """,
      """
      def goodNodes(root):
          def dfs(node, max_so_far):
              if not node:
                  return 0
              good = 1 if node.val >= max_so_far else 0
              max_so_far = max(max_so_far, node.val)
              good += dfs(node.left, max_so_far)
              good += dfs(node.right, max_so_far)
              return good

          return dfs(root, root.val)
      """,
      "goodNodes(build_tree([3, 1, 4, 3, None, 1, 5]))",
      "4"),

    p(98, "Validate Binary Search Tree", "Medium",
      """
      Is this a valid BST (every left subtree < node < every right subtree)?
      Idea: pass down the allowed (low, high) range; it narrows at each step.
      """,
      """
      def isValidBST(root):
          def valid(node, low, high):
              if not node:
                  return True
              if not (low < node.val < high):
                  return False
              return valid(node.left, low, node.val) and valid(node.right, node.val, high)

          return valid(root, float("-inf"), float("inf"))
      """,
      "isValidBST(build_tree([5, 1, 6, None, None, 3, 7]))",
      "False"),

    p(230, "Kth Smallest Element in a BST", "Medium",
      """
      Return the k-th smallest value.
      Idea: in-order traversal visits a BST in sorted order; stop at the k-th.
      """,
      """
      def kthSmallest(root, k):
          stack = []
          curr = root
          while stack or curr:
              while curr:
                  stack.append(curr)
                  curr = curr.left
              curr = stack.pop()
              k -= 1
              if k == 0:
                  return curr.val
              curr = curr.right
      """,
      "kthSmallest(build_tree([5, 3, 6, 2, 4, None, None, 1]), 3)",
      "3"),

    p(105, "Construct Binary Tree from Preorder and Inorder Traversal", "Medium",
      """
      Rebuild the tree from its preorder and inorder lists.
      Idea: preorder's next value is the root; its position in inorder splits
      the left subtree from the right subtree.
      """,
      """
      def buildTree(preorder, inorder):
          index = {val: i for i, val in enumerate(inorder)}
          pre_i = 0

          def build(l, r):  # builds the subtree for inorder[l..r]
              nonlocal pre_i
              if l > r:
                  return None
              root = TreeNode(preorder[pre_i])
              pre_i += 1
              mid = index[root.val]
              root.left = build(l, mid - 1)
              root.right = build(mid + 1, r)
              return root

          return build(0, len(inorder) - 1)
      """,
      "buildTree([3, 9, 20, 15, 7], [9, 3, 15, 20, 7])",
      "[3, 9, 20, None, None, 15, 7]"),

    p(124, "Binary Tree Maximum Path Sum", "Hard",
      """
      Max sum of any path (it may bend once at a node).
      Idea: gain(node) = best downward path from node. A path bending at
      node is node.val + left gain + right gain. Ignore negative gains.
      """,
      """
      def maxPathSum(root):
          best = root.val

          def gain(node):
              nonlocal best
              if not node:
                  return 0
              left = max(gain(node.left), 0)
              right = max(gain(node.right), 0)
              best = max(best, node.val + left + right)
              return node.val + max(left, right)

          gain(root)
          return best
      """,
      "maxPathSum(build_tree([-10, 9, 20, None, None, 15, 7]))",
      "42"),

    p(297, "Serialize and Deserialize Binary Tree", "Hard",
      """
      Turn a tree into a string and back.
      Idea: preorder DFS writing "N" for empty children; reading the values
      back in the same order rebuilds the exact shape.
      """,
      """
      def serialize(root):
          res = []

          def dfs(node):
              if not node:
                  res.append("N")
                  return
              res.append(str(node.val))
              dfs(node.left)
              dfs(node.right)

          dfs(root)
          return ",".join(res)

      def deserialize(data):
          vals = data.split(",")
          i = 0

          def dfs():
              nonlocal i
              if vals[i] == "N":
                  i += 1
                  return None
              node = TreeNode(int(vals[i]))
              i += 1
              node.left = dfs()
              node.right = dfs()
              return node

          return dfs()
      """,
      """
      data = serialize(build_tree([1, 2, 3, None, None, 4, 5]))
      deserialize(data)
      """,
      "[1, 2, 3, None, None, 4, 5]"),
]
