from typing import List

"""
    1.单序列双指针
"""


class TwoPointers:
    """
        1.1 相向双指针
    """

    # 1750 Minimum Length of String After Deleting Similar Ends
    def minimumLength(self, s: str) -> int:
        left, right = 0, len(s) - 1
        while left < right and s[left] == s[right]:
            c = s[left]
            while left <= right and s[left] == c:
                left += 1
            while right >= left and s[right] == c:
                right -= 1
        return right - left + 1

    # 658 Find K Closest Elements
    def findClosestElements(self, arr: List[int], k: int, x: int) -> List[int]:
        left, right = 0, len(arr) - 1

        while left < right:
            if right - left + 1 == k:
                break
            if abs(arr[left] - x) <= abs(arr[right] - x):
                right -= 1
            else:
                left += 1
        return arr[left:right + 1]

    # 167 Two Sum II - Input Array Is Sorted
    def twoSum(self, numbers: List[int], target: int) -> List[int]:
        left, right = 0, len(numbers) - 1

        while left < right:
            if numbers[left] + numbers[right] < target:
                left += 1
            elif numbers[left] + numbers[right] > target:
                right -= 1
            else:
                return [left, right]

        return []

    # 2563 Count the Number of Fair Pairs
    def countFairPairs(self, nums: List[int], lower: int, upper: int) -> int:
        pass

    # LCP28 采购方案
    def purchasePlans(self, nums: List[int], target: int) -> int:
        left, right = 0, len(nums) - 1
        nums.sort()

        ans = 0
        while left < right:
            while left < right and nums[left] + nums[right] > target:
                right -= 1
            ans += (right - left) % 1000000007
            left += 1
        return ans

    def threeSumMulti(self, arr: List[int], target: int) -> int:
        arr.sort()
        ans = 0

        for i, a in enumerate(arr):
            left, right = i + 1, len(arr) - 1
            t = target - a
            if t <= 0:
                continue
            while left < right:
                if arr[left] + arr[right] < t:
                    left += 1
                elif arr[left] + arr[right] > t:
                    right -= 1
                else:
                    tl, tr = left, right
                    al, ar = arr[left], arr[right]
                    while left < right and arr[left] == al:
                        left += 1
                    while right >= left and arr[right] == ar:
                        right -= 1
                    ans = (ans + (left - tl) * (tr - right)) % 1000000007

        return ans


if __name__ == '__main__':
    slu = TwoPointers()
    # slu.minimumLength("aabccabba")
    ans = slu.threeSumMulti([1, 1, 2, 2, 3, 3, 4, 4, 5, 5], 8)
    print(ans)
    pass
