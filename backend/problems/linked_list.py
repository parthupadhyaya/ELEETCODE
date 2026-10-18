from ._base import p

CATEGORY = "Linked List"

PROBLEMS = [
    p(206, "Reverse Linked List", "Easy",
      """
      Reverse a singly linked list.
      Idea: walk the list, pointing each node's next back at prev.
      Save curr.next first so you don't lose the rest of the list.
      """,
      """
      def reverseList(head):
          prev, curr = None, head
          while curr:
              nxt = curr.next
              curr.next = prev
              prev = curr
              curr = nxt
          return prev
      """,
      "reverseList(build_list([1, 2, 3, 4, 5]))",
      "[5, 4, 3, 2, 1]"),

    p(21, "Merge Two Sorted Lists", "Easy",
      """
      Merge two sorted linked lists into one sorted list.
      Idea: a dummy head plus a tail pointer; always attach the smaller node.
      """,
      """
      def mergeTwoLists(list1, list2):
          dummy = tail = ListNode()
          while list1 and list2:
              if list1.val < list2.val:
                  tail.next = list1
                  list1 = list1.next
              else:
                  tail.next = list2
                  list2 = list2.next
              tail = tail.next
          tail.next = list1 or list2
          return dummy.next
      """,
      "mergeTwoLists(build_list([1, 2, 4]), build_list([1, 3, 4]))",
      "[1, 1, 2, 3, 4, 4]"),

    p(141, "Linked List Cycle", "Easy",
      """
      Does the list loop back on itself?
      Idea: Floyd's tortoise and hare. fast moves 2 steps, slow moves 1;
      if there's a cycle they must meet.
      """,
      """
      def hasCycle(head):
          slow, fast = head, head
          while fast and fast.next:
              slow = slow.next
              fast = fast.next.next
              if slow is fast:
                  return True
          return False
      """,
      "hasCycle(build_list([3, 2, 0, -4], cycle_at=1))",
      "True"),

    p(143, "Reorder List", "Medium",
      """
      Reorder L0 -> L1 -> ... -> Ln into L0 -> Ln -> L1 -> Ln-1 -> ...
      Idea: find the middle (slow/fast), reverse the second half, then
      weave the two halves together.
      """,
      """
      def reorderList(head):
          # 1. find the middle
          slow, fast = head, head.next
          while fast and fast.next:
              slow = slow.next
              fast = fast.next.next
          # 2. reverse the second half
          second = slow.next
          slow.next = None
          prev = None
          while second:
              nxt = second.next
              second.next = prev
              prev = second
              second = nxt
          # 3. weave the halves together
          first, second = head, prev
          while second:
              tmp1, tmp2 = first.next, second.next
              first.next = second
              second.next = tmp1
              first, second = tmp1, tmp2
          return head
      """,
      "reorderList(build_list([1, 2, 3, 4, 5]))",
      "[1, 5, 2, 4, 3]"),

    p(19, "Remove Nth Node From End of List", "Medium",
      """
      Remove the n-th node from the end in one pass.
      Idea: move right n steps ahead, then move both until right falls off.
      left then sits just before the node to delete.
      """,
      """
      def removeNthFromEnd(head, n):
          dummy = ListNode(0, head)
          left, right = dummy, head
          for _ in range(n):
              right = right.next
          while right:
              left = left.next
              right = right.next
          left.next = left.next.next
          return dummy.next
      """,
      "removeNthFromEnd(build_list([1, 2, 3, 4, 5]), 2)",
      "[1, 2, 3, 5]"),

    p(138, "Copy List with Random Pointer", "Medium",
      """
      Deep-copy a list whose nodes also have a random pointer.
      Idea: pass 1 creates a copy of every node in a hashmap old -> new;
      pass 2 wires next and random using that map.
      """,
      """
      class Node:
          def __init__(self, val, next=None, random=None):
              self.val = val
              self.next = next
              self.random = random

      def copyRandomList(head):
          old_to_new = {None: None}
          curr = head
          while curr:
              old_to_new[curr] = Node(curr.val)
              curr = curr.next
          curr = head
          while curr:
              copy = old_to_new[curr]
              copy.next = old_to_new[curr.next]
              copy.random = old_to_new[curr.random]
              curr = curr.next
          return old_to_new[head]
      """,
      """
      a, b, c = Node(7), Node(13), Node(11)
      a.next, b.next = b, c
      b.random, c.random = a, a
      copy = copyRandomList(a)
      [(n.val, n.random.val if n.random else None) for n in (copy, copy.next, copy.next.next)]
      """,
      "[(7, None), (13, 7), (11, 7)]"),

    p(2, "Add Two Numbers", "Medium",
      """
      Digits are stored in reverse order; add the two numbers.
      Idea: grade-school addition, one node at a time, carrying the tens.
      """,
      """
      def addTwoNumbers(l1, l2):
          dummy = tail = ListNode()
          carry = 0
          while l1 or l2 or carry:
              v1 = l1.val if l1 else 0
              v2 = l2.val if l2 else 0
              total = v1 + v2 + carry
              carry = total // 10
              tail.next = ListNode(total % 10)
              tail = tail.next
              l1 = l1.next if l1 else None
              l2 = l2.next if l2 else None
          return dummy.next
      """,
      "addTwoNumbers(build_list([2, 4, 3]), build_list([5, 6, 4]))",
      "[7, 0, 8]"),

    p(287, "Find the Duplicate Number", "Medium",
      """
      n + 1 numbers in [1, n]; find the repeated one with O(1) memory.
      Idea: treat i -> nums[i] as a linked list. The duplicate is where the
      cycle starts: Floyd's slow/fast meet, then a second walker from 0
      meets slow at the cycle entrance.
      """,
      """
      def findDuplicate(nums):
          slow = fast = 0
          while True:
              slow = nums[slow]
              fast = nums[nums[fast]]
              if slow == fast:
                  break
          slow2 = 0
          while slow != slow2:
              slow = nums[slow]
              slow2 = nums[slow2]
          return slow
      """,
      "findDuplicate([1, 3, 4, 2, 2])",
      "2"),

    p(146, "LRU Cache", "Medium",
      """
      A fixed-size cache that evicts the least recently used key, O(1) ops.
      Idea: hashmap key -> node, plus a doubly linked list ordered by use.
      left.next is the LRU entry, right.prev the most recent.
      """,
      """
      class DNode:
          def __init__(self, key, val):
              self.key, self.val = key, val
              self.prev = self.next = None

      class LRUCache:
          def __init__(self, capacity):
              self.cap = capacity
              self.cache = {}  # key -> node
              # left = least recently used, right = most recently used
              self.left, self.right = DNode(0, 0), DNode(0, 0)
              self.left.next, self.right.prev = self.right, self.left

          def remove(self, node):
              prev, nxt = node.prev, node.next
              prev.next, nxt.prev = nxt, prev

          def insert(self, node):
              prev, nxt = self.right.prev, self.right
              prev.next = nxt.prev = node
              node.next, node.prev = nxt, prev

          def get(self, key):
              if key in self.cache:
                  self.remove(self.cache[key])
                  self.insert(self.cache[key])
                  return self.cache[key].val
              return -1

          def put(self, key, value):
              if key in self.cache:
                  self.remove(self.cache[key])
              self.cache[key] = DNode(key, value)
              self.insert(self.cache[key])
              if len(self.cache) > self.cap:
                  lru = self.left.next
                  self.remove(lru)
                  del self.cache[lru.key]
      """,
      """
      lru = LRUCache(2)
      lru.put(1, 1)
      lru.put(2, 2)
      out = [lru.get(1)]
      lru.put(3, 3)
      out.append(lru.get(2))
      lru.put(4, 4)
      out += [lru.get(1), lru.get(3), lru.get(4)]
      out
      """,
      "[1, -1, -1, 3, 4]"),

    p(23, "Merge k Sorted Lists", "Hard",
      """
      Merge k sorted linked lists.
      Idea: a min-heap holds the current head of every list; pop the
      smallest, attach it, push its successor.
      """,
      """
      def mergeKLists(lists):
          heap = []
          for i, node in enumerate(lists):
              if node:
                  heapq.heappush(heap, (node.val, i, node))
          dummy = tail = ListNode()
          while heap:
              val, i, node = heapq.heappop(heap)
              tail.next = node
              tail = node
              if node.next:
                  heapq.heappush(heap, (node.next.val, i, node.next))
          return dummy.next
      """,
      "mergeKLists([build_list([1, 4, 5]), build_list([1, 3, 4]), build_list([2, 6])])",
      "[1, 1, 2, 3, 4, 4, 5, 6]"),

    p(25, "Reverse Nodes in k-Group", "Hard",
      """
      Reverse every consecutive group of k nodes.
      Idea: find the k-th node of the next group; if it exists, reverse the
      group in place and reconnect it to the previous group.
      """,
      """
      def reverseKGroup(head, k):
          dummy = ListNode(0, head)
          group_prev = dummy
          while True:
              kth = group_prev
              for _ in range(k):
                  kth = kth.next
                  if not kth:
                      return dummy.next
              group_next = kth.next
              # reverse this group
              prev, curr = group_next, group_prev.next
              while curr is not group_next:
                  nxt = curr.next
                  curr.next = prev
                  prev = curr
                  curr = nxt
              first = group_prev.next
              group_prev.next = kth
              group_prev = first
      """,
      "reverseKGroup(build_list([1, 2, 3, 4, 5]), 2)",
      "[2, 1, 4, 3, 5]"),
]
