from collections import defaultdict, Counter
from typing import List


class SlidingWindow:
    # 3 Longest Substring Without Repeating Characters
    def maximumLengthSubstring(self, s: str) -> int:
        ans = left = 0
        cnt = defaultdict(int)
        for i, c in enumerate(s):
            cnt[c] += 1
            while cnt[c] > 2:
                cnt[s[left]] -= 1
                left += 1
            ans = max(ans, i - left + 1)
        return ans

    # 2024 Maximize the Confusion of an Exam
    def maxConsecutiveAnswers(self, answerKey: str, k: int) -> int:
        ans = left = 0
        cnt = defaultdict(int)

        for i, c in enumerate(answerKey):
            cnt[c] += 1
            while cnt['T'] > k and cnt['F'] > k:
                cnt[answerKey[left]] -= 1
                left += 1
            ans = max(ans, i - left + 1)

        return ans

    # 1004 Max Consecutive Ones III
    def longestOnes(self, nums: List[int], k: int) -> int:
        result = left = 0
        count = defaultdict(int)

        for i, num in enumerate(nums):
            count[nums[i]] += 1
            while count[0] > k:
                count[nums[left]] -= 1
                left += 1
            result = max(result, i - left + 1)
        return result

    # 1658 Minimum Operations to Reduce X to Zero
    def minOperations(self, nums: List[int], x: int) -> int:
        target = sum(nums) - x
        if target < 0:
            return -1

        ans = -1
        s = left = 0
        for right, x in enumerate(nums):
            s += x
            while s > target:
                s -= nums[left]
                left += 1  # 缩小子数组长度
            if s == target:
                ans = max(ans, right - left + 1)
        return -1 if ans < 0 else len(nums) - ans

    # 2516 Minimum Time to Take K Characters from the End
    def takeCharacters(self, s: str, k: int) -> int:
        # 计算原始字符数量
        counter = Counter(s)

        # 检查是否有足够的字符
        if any(counter[c] < k for c in 'abc'):
            return -1

        n = len(s)
        left = 0
        max_keep = 0
        remaining = {c: counter[c] - k for c in 'abc'}  # 可以保留在窗口内的字符数量

        for right in range(n):
            # 右指针移动，窗口扩大
            remaining[s[right]] -= 1

            # 如果某个字符超出限制，移动左指针直到满足条件
            while left <= right and any(remaining[c] < 0 for c in 'abc'):
                remaining[s[left]] += 1
                left += 1

            # 更新最大保留长度
            max_keep = max(max_keep, right - left + 1)

        return n - max_keep

if __name__ == '__main__':
    sol = SlidingWindow()
    res = sol.takeCharacters("aabaaaacaabc", 2)
    print(res)
