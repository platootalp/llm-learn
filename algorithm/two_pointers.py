class TwoPointers:
    """
        1.单序列双指针
    """
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


if __name__ == '__main__':
    slu = TwoPointers()
    slu.minimumLength("aabccabba")
    pass
