在 Java 领域，接口幂等性（Idempotency）是指**对同一请求的多次调用，结果应当保持一致，且不会对系统产生额外的副作用**。  
常见的幂等性实现方案如下：

---

## **1. 通过数据库唯一索引**
### **适用场景**
- 订单去重、消息去重等
- 适用于写入类操作（如新增订单）

### **实现方式**
使用**唯一约束**保证同一业务请求不会被重复执行。例如，在订单表 (`orders`) 中，使用 `request_id` 作为唯一索引：

```sql
CREATE TABLE orders (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    request_id VARCHAR(64) UNIQUE NOT NULL, -- 唯一请求 ID
    user_id BIGINT NOT NULL,
    amount DECIMAL(10,2) NOT NULL,
    status VARCHAR(20) NOT NULL
);
```
然后，在插入数据时，通过 `request_id` 防止重复提交：

```java
public boolean createOrder(String requestId, Long userId, BigDecimal amount) {
    try {
        orderRepository.insertOrder(requestId, userId, amount);
        return true;
    } catch (DuplicateKeyException e) {
        // 已存在相同 request_id，说明是重复请求
        return false;
    }
}
```

**优点**：
- 实现简单，适用于写入类操作
- 直接利用数据库唯一性约束，无需额外存储

**缺点**：
- 需要数据库支持（唯一索引）
- 并发量大时可能存在数据库压力

---

## **2. 通过分布式锁**
### **适用场景**
- 需要严格串行化的操作，如扣库存

### **实现方式**
使用 **Redis 分布式锁** 防止并发请求导致数据不一致：
```java
public boolean deductStock(Long productId, int quantity) {
    String lockKey = "lock:stock:" + productId;
    boolean lock = redisTemplate.opsForValue().setIfAbsent(lockKey, "locked", 10, TimeUnit.SECONDS);
    
    if (!lock) {
        return false; // 获取锁失败，说明已有请求在处理中
    }

    try {
        // 扣减库存
        stockService.reduceStock(productId, quantity);
        return true;
    } finally {
        redisTemplate.delete(lockKey);
    }
}
```

**优点**：
- 适用于严格的串行化场景（如库存扣减）
- 可避免高并发情况下数据错误

**缺点**：
- 需要依赖 Redis
- 存在**锁超时**和**死锁**风险，需保证**锁过期时间合适**（推荐使用 `Redisson`）

---

## **3. 通过 Token 机制（业务去重）**
### **适用场景**
- 适用于接口幂等性保证，如支付、订单提交等
- 适用于前端、后端交互的 API 请求

### **实现方式**
1. 客户端**先请求**获取 `token`（通常是 UUID）：
    ```java
    String token = UUID.randomUUID().toString();
    redisTemplate.opsForValue().set("idempotency:" + token, "1", 5, TimeUnit.MINUTES);
    ```
2. 客户端在后续请求时，**带上 token**：
    ```http
    POST /api/order
    Header: Idempotency-Token: 123e4567-e89b-12d3-a456-426614174000
    ```
3. 服务器端验证 `token`，防止重复提交：
    ```java
    public boolean createOrder(String token, Long userId, BigDecimal amount) {
        Boolean exists = redisTemplate.delete("idempotency:" + token);
        if (Boolean.FALSE.equals(exists)) {
            return false; // token 已使用或不存在
        }

        orderService.createOrder(userId, amount);
        return true;
    }
    ```

**优点**：
- **避免重复请求**，特别适用于支付类接口
- **高效可扩展**，Redis 读取速度快

**缺点**：
- 需要前端/客户端配合
- 需要额外存储 `token`

---

## **4. 通过幂等状态机**
### **适用场景**
- 适用于**状态变更类**操作（如订单状态流转）

### **实现方式**
- 订单从 `INIT` → `PAID` → `SHIPPED`，需要幂等性控制
- 只有**满足状态流转条件**时，才允许修改：
```java
@Transactional
public boolean updateOrderStatus(Long orderId, String newStatus) {
    Order order = orderRepository.findById(orderId);
    if (!canTransition(order.getStatus(), newStatus)) {
        return false; // 状态不合法，幂等性检查失败
    }
    
    orderRepository.updateStatus(orderId, newStatus);
    return true;
}

private boolean canTransition(String currentStatus, String newStatus) {
    Map<String, List<String>> validTransitions = Map.of(
        "INIT", List.of("PAID"),
        "PAID", List.of("SHIPPED")
    );
    return validTransitions.getOrDefault(currentStatus, List.of()).contains(newStatus);
}
```

**优点**：
- 适用于**状态流转**业务，天然幂等
- **逻辑清晰**，易扩展

**缺点**：
- 仅适用于**状态流转**业务

---

## **5. 通过幂等请求缓存**
### **适用场景**
- 适用于**计算类**、**查询类**接口（如汇总统计）

### **实现方式**
请求执行前，先检查**是否已有相同结果**：
```java
public BigDecimal getTotalRevenue(Long shopId, String month) {
    String cacheKey = "revenue:" + shopId + ":" + month;
    
    BigDecimal cachedResult = redisTemplate.opsForValue().get(cacheKey);
    if (cachedResult != null) {
        return cachedResult; // 直接返回缓存结果，避免重复计算
    }

    BigDecimal revenue = orderRepository.getTotalRevenue(shopId, month);
    redisTemplate.opsForValue().set(cacheKey, revenue, 10, TimeUnit.MINUTES);
    return revenue;
}
```

**优点**：
- 避免重复计算，提升接口性能

**缺点**：
- 需要定期清理缓存

---

## **总结**
| 方案 | 适用场景 | 依赖 | 复杂度 | 优缺点 |
|------|---------|------|------|------|
| **数据库唯一索引** | 订单去重、消息去重 | 数据库 | 低 | ✅简单高效，但依赖数据库 |
| **分布式锁** | 扣库存、限流 | Redis | 中 | ✅避免并发问题，但可能影响性能 |
| **Token 机制** | 前端请求去重 | Redis | 中 | ✅灵活扩展，适合 API 幂等性 |
| **状态机控制** | 状态流转 | 业务逻辑 | 高 | ✅避免非法状态变更 |
| **缓存查询结果** | 计算、统计接口 | Redis | 低 | ✅高性能，适用于查询类接口 |

🔹 **推荐方案：**
- **写操作（新增类）：** ✅**数据库唯一索引** / **Token 机制**
- **更新操作（修改类）：** ✅**状态机控制** / **分布式锁**
- **查询操作（计算类）：** ✅**缓存**

你现在是在哪个业务场景下需要幂等性呢？可以细化一下具体需求，我可以帮你优化方案！ 😊