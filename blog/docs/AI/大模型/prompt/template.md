
### 1. 代码优化
**指令**：请优化以下 Java 代码，提高性能并符合最佳实践。

**上下文**：该代码用于处理用户请求，当前执行速度较慢，可能存在性能瓶颈。

**输入数据**：

```java
public List<String> getUsernames(List<User> users) {
    List<String> usernames = new ArrayList<>();
    for (User user : users) {
        usernames.add(user.getUsername());
    }
    return usernames;
}
```
**输出指示**：请提供优化后的代码，并详细解释优化点。

---

### 2. 异常调试
**指令**：请分析以下 Java 异常信息，并提供可能的修复方案。

**上下文**：异常发生在 Spring Boot 项目运行过程中，怀疑与数据库访问操作有关。

**输入数据**：

```plaintext
org.springframework.dao.DataIntegrityViolationException: 
could not execute statement; SQL [n/a]; constraint [null]; 
nested exception is org.hibernate.exception.ConstraintViolationException
```
输出指示：请详细解释异常可能原因，并提供修复方案。

---

### 3. 设计模式推荐
**指令**：请推荐适合以下场景的设计模式，并提供实现示例。

**上下文**：我正在开发一个 Spring Boot 应用，需要一个灵活扩展的日志存储方案，支持本地文件、数据库和云存储。

**输入数据**：无

**输出指示**：请推荐合适的设计模式（如策略模式、工厂模式等），并给出相应的代码示例。

---

### 4. SQL 查询优化

**指令**：请优化以下 SQL 查询，以提高查询效率。

**上下文**：查询在 MySQL 数据库中执行，数据量大且响应较慢。

**输入数据**：

```sql
SELECT * FROM orders WHERE status = 'COMPLETED' ORDER BY created_at;
```

**输出指示**：请提供优化建议，并给出优化后的 SQL 语句。



---

### 5. 数据库表生成实体类

**指令**：请根据以下数据库表结构生成对应的 Java 实体类，要求使用 JPA 注解。

**上下文**：数据库采用 MySQL，表结构信息如下：

**输入数据**：

```sql
CREATE TABLE user (
    id BIGINT PRIMARY KEY AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    email VARCHAR(100) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

**输出指示**：请提供对应的 Java 实体类代码，并注明各字段含义及Mybatis-plus注解。

