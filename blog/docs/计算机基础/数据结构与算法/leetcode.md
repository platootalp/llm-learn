# 算法

[灵神题单](https://leetcode.cn/discuss/post/3141566/ru-he-ke-xue-shua-ti-by-endlesscheng-q3yd/)

## 1. 滑动窗口
### 1.1 定长滑窗

#### 步骤

入-更新-出

入：下标为 i 的元素进入窗口，更新相关统计量。如果 `i<k-1` 则重复第一步

更新：更新答案。一般是更新最大值/最小值

出：下标为 `i-k+1` 的元素离开窗口，更新相关统计量

#### 实现

```java
public static <T> void slidingWindow(List<T> data, int windowSize,
										 Consumer<T> add,
										 Consumer<T> remove,
										 Runnable process,
										 Supplier<Boolean> isValid) {
		int left = 0;
		for (int right = 0; right < data.size(); right++) {
			add.accept(data.get(right));

			if (right < windowSize - 1)
				continue;

			if (isValid.get())
				process.run();

			remove.accept(data.get(left));
			left++;
		}
	}

public int divisorSubstrings(int num, int k) {
		String s = String.valueOf(num);
		List<Character> data = s.chars()
				.mapToObj(c -> (char) c)
				.collect(Collectors.toList());
		StringBuilder windowStr = new StringBuilder();
		int[] result = {0};

		slidingWindow(data, k,
				(c) -> windowStr.append(c),
				(c) -> windowStr.deleteCharAt(0),
				() -> result[0]++,
				() -> {
					int windowNum = Integer.parseInt(windowStr.toString());
					return windowNum != 0 && num % windowNum == 0;
				}
		);

		return result[0];
	}
```

### 1.2 不定长滑动窗口

#### 分类

不定长滑动窗口主要分为三类：求最长子数组，求最短子数组，以及求子数组个数

#### 求最长/最大子数组

##### 步骤

1.设置左右指针分别为left = right = 0

2.右指针滑动，同时记录目标值变化

3.当条件不满足时让左指针不断右滑直到窗口内的元素满足条件，记录左右指针的间隔

##### 实现

```python
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
```







