from collections import defaultdict
from typing import Optional, List


class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next


class Solution:
    """
        遍历链表
    """

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

    """
        删除节点
    """

    # 203 移除链表元素
    def removeElements(self, head: Optional[ListNode], val: int) -> Optional[ListNode]:
        dummy = ListNode(0)
        dummy.next = head
        p = dummy

        while p.next:
            if p.next.val == val:
                p.next = p.next.next
            else:
                p = p.next

        return dummy.next

    # 3217
    def modifiedList(self, nums: List[int], head: Optional[ListNode]) -> Optional[ListNode]:
        dummy = ListNode(0)
        dummy.next = head

        p = dummy
        dit = set(nums)

        while p.next:
            if p.next.val in dit:
                p.next = p.next.next
            else:
                p = p.next

        return dummy.next
