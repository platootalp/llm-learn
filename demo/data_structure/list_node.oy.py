from collections import defaultdict
from typing import Optional, List


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    # 1290 二进制链表转整数
    def getDecimalValue(self, head: Optional[ListNode]) -> int:
        ans = 0
        p = head
        while p != None:
            ans += ans * 2 + p.val
            p = p.next
        return ans

    # 725
    def splitListToParts(self, head: Optional[ListNode], k: int) -> List[Optional[ListNode]]:
        # Step 1: Get the length of the list
        length = 0
        cur = head
        while cur:
            length += 1
            cur = cur.next

        # Step 2: Determine size of each part
        part_size = length // k
        remainder = length % k  # Extra nodes to distribute

        res = []
        current = head
        for i in range(k):
            part_head = current
            current_part_size = part_size + (1 if i < remainder else 0)

            # Traverse current part
            for j in range(current_part_size - 1):
                if current:
                    current = current.next

            # Cut the list
            if current:
                next_part = current.next
                current.next = None
                current = next_part

            res.append(part_head)

        return res

    # 817 链表组件
    def numComponents(self, head: Optional[ListNode], nums: List[int]) -> int:
        dict = defaultdict()
        for num in nums:
            dict[num] += 1



