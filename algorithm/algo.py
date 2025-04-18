from collections import defaultdict
from typing import List


class Solution:
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

    # 2779 Maximum Beauty of an Array After Applying Operation
    def maximumBeauty(self, nums: List[int], k: int) -> int:
        pass

if __name__ == '__main__':
    sol = Solution()
    res = sol.maximumLengthSubstring("aababcabc")
    print(res)
