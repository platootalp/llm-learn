class Solution:
    # 第448场周赛
    # 3536
    def maxProduct(n: int) -> int:
        digits = [int(c) for c in str(n)]
        digits.sort(reverse=True)
        return digits[0] * digits[1]



if __name__ == '__main__':
    pass
