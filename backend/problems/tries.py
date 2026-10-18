from ._base import p

CATEGORY = "Tries"

PROBLEMS = [
    p(208, "Implement Trie (Prefix Tree)", "Medium",
      """
      insert(word), search(word) and startsWith(prefix).
      Idea: each node maps a character to a child node; `end` marks nodes
      where a whole word finishes.
      """,
      """
      class TrieNode:
          def __init__(self):
              self.children = {}
              self.end = False

      class Trie:
          def __init__(self):
              self.root = TrieNode()

          def insert(self, word):
              node = self.root
              for ch in word:
                  if ch not in node.children:
                      node.children[ch] = TrieNode()
                  node = node.children[ch]
              node.end = True

          def search(self, word):
              node = self.root
              for ch in word:
                  if ch not in node.children:
                      return False
                  node = node.children[ch]
              return node.end

          def startsWith(self, prefix):
              node = self.root
              for ch in prefix:
                  if ch not in node.children:
                      return False
                  node = node.children[ch]
              return True
      """,
      """
      trie = Trie()
      trie.insert("apple")
      out = [trie.search("apple"), trie.search("app"), trie.startsWith("app")]
      trie.insert("app")
      out.append(trie.search("app"))
      out
      """,
      "[True, False, True, True]"),

    p(211, "Design Add and Search Words Data Structure", "Medium",
      """
      Like a trie, but search may contain '.' which matches any letter.
      Idea: on '.', try every child (DFS); otherwise follow one child.
      """,
      """
      class TrieNode:
          def __init__(self):
              self.children = {}
              self.end = False

      class WordDictionary:
          def __init__(self):
              self.root = TrieNode()

          def addWord(self, word):
              node = self.root
              for ch in word:
                  node = node.children.setdefault(ch, TrieNode())
              node.end = True

          def search(self, word):
              def dfs(i, node):
                  if i == len(word):
                      return node.end
                  ch = word[i]
                  if ch == ".":
                      for child in node.children.values():
                          if dfs(i + 1, child):
                              return True
                      return False
                  if ch not in node.children:
                      return False
                  return dfs(i + 1, node.children[ch])

              return dfs(0, self.root)
      """,
      """
      wd = WordDictionary()
      for w in ["bad", "dad", "mad"]:
          wd.addWord(w)
      [wd.search("pad"), wd.search("bad"), wd.search(".ad"), wd.search("b..")]
      """,
      "[False, True, True, True]"),

    p(212, "Word Search II", "Hard",
      """
      Find every word from the list that can be traced on the board.
      Idea: put all words in a trie and DFS the board once, following trie
      children. Dead-end prefixes stop the search immediately.
      """,
      """
      class TrieNode:
          def __init__(self):
              self.children = {}
              self.word = None

      def findWords(board, words):
          root = TrieNode()
          for w in words:
              node = root
              for ch in w:
                  node = node.children.setdefault(ch, TrieNode())
              node.word = w

          rows, cols = len(board), len(board[0])
          res = []

          def dfs(r, c, node):
              if r < 0 or c < 0 or r >= rows or c >= cols:
                  return
              ch = board[r][c]
              if ch not in node.children:
                  return
              node = node.children[ch]
              if node.word:
                  res.append(node.word)
                  node.word = None  # found it; don't add it twice
              board[r][c] = "#"  # mark as used on this path
              for dr, dc in ((1, 0), (-1, 0), (0, 1), (0, -1)):
                  dfs(r + dr, c + dc, node)
              board[r][c] = ch

          for r in range(rows):
              for c in range(cols):
                  dfs(r, c, root)
          return res
      """,
      'findWords([["o", "a", "a", "n"], ["e", "t", "a", "e"], ["i", "h", "k", "r"]], ["oath", "pea", "eat", "rain"])',
      "['oath', 'eat']"),
]
