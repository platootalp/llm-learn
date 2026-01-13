# 项目文档目录

## 📚 文档组织结构

本目录包含 Engineer 项目的所有技术文档，按模块组织。

### 📁 目录结构

```
docs/project/
├── README.md           # 本文件 - 文档索引
└── tools/              # 工具系统文档
    ├── INDEX.md        # 工具文档索引
    ├── QUICK_START.md  # 快速上手指南
    ├── README.md       # 完整使用文档
    └── IMPLEMENTATION.md # 实现报告
```

### 🗂️ 模块文档

#### 1. 工具系统 (Tools)

**位置**: `tools/`

**文档列表**:
- [INDEX.md](./tools/INDEX.md) - 文档索引和导航
- [QUICK_START.md](./tools/QUICK_START.md) - 快速上手指南
- [README.md](./tools/README.md) - 完整使用文档
- [IMPLEMENTATION.md](./tools/IMPLEMENTATION.md) - 实现报告

**简介**: 
提供完整的工具集成框架，参考 LangChain 设计，为 LLM 应用提供灵活的工具调用能力。包含11个内置工具、装饰器系统、工具管理器等完整功能。

**快速开始**: [tools/QUICK_START.md](./tools/QUICK_START.md)

---

### 🎯 使用指南

#### 如果你是新用户
1. 浏览本文件了解项目结构
2. 进入感兴趣的模块目录
3. 阅读该模块的 `QUICK_START.md` 快速上手
4. 深入学习 `README.md` 了解完整功能

#### 如果你是开发者
1. 浏览本文件了解整体架构
2. 阅读各模块的 `README.md` 了解设计
3. 参考 `IMPLEMENTATION.md` 了解实现细节
4. 查看示例代码和测试用例

#### 如果你是维护者
1. 阅读 `IMPLEMENTATION.md` 了解技术栈
2. 查看代码统计和架构设计
3. 参考测试用例进行验证
4. 根据需要扩展功能

---

### 📊 项目统计

#### 整体统计
- **模块数**: 1个（工具系统）
- **核心文件**: 6个
- **代码行数**: ~2000行
- **文档字数**: ~24000字
- **示例代码**: 100+个

#### 工具系统统计
- **核心类**: 10+个
- **内置工具**: 11个
- **装饰器**: 3个
- **单元测试**: 30+个

---

### 🔗 快速链接

#### 工具系统
- [快速开始](./tools/QUICK_START.md)
- [完整文档](./tools/README.md)
- [实现报告](./tools/IMPLEMENTATION.md)

#### 代码位置
- 工具系统: `src/core/tools/`
- 示例代码: `examples/tools_*.py`
- 测试代码: `tests/test_tools.py`

---

### 📝 文档规范

#### 文档命名
- `README.md` - 模块的完整使用文档
- `QUICK_START.md` - 快速上手指南
- `IMPLEMENTATION.md` - 实现报告和技术细节
- `INDEX.md` - 文档索引和导航

#### 目录组织
```
docs/project/
└── <模块名>/
    ├── INDEX.md
    ├── QUICK_START.md
    ├── README.md
    └── IMPLEMENTATION.md
```

#### 文档更新
- 每次功能更新后需同步更新文档
- 保持文档与代码一致
- 更新版本号和更新日期

---

### 🔄 版本信息

- **文档版本**: 1.0.0
- **最后更新**: 2026-01-13
- **状态**: ✅ 当前

---

### 📞 文档维护

如需补充或更新文档：
1. 在对应模块目录下创建或修改文档
2. 更新本索引文件
3. 确保文档格式符合规范
4. 更新版本信息

---

**开始探索**: [工具系统文档 →](./tools/INDEX.md)

