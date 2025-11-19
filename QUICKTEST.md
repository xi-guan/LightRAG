# LightRAG 三语言实体提取器 - 快速测试指南

## 🎯 测试 LightRAG Server (推荐)

### 最快方式（2 步）

```bash
# 步骤 1: 启动服务器（自动安装所有依赖和模型）
./scripts/start_server_with_trilingual.sh

# 步骤 2: 新开终端，运行测试
uv run python examples/test_server_trilingual.py
```

就这么简单！✅

---

## 📝 详细测试流程

### 选项 A: 服务器测试（推荐用于生产环境）

#### 1. 启动服务器

```bash
# 方式 1: 一键启动（推荐）
./scripts/start_server_with_trilingual.sh

# 方式 2: 手动启动
uv sync --extra api --extra trilingual
./scripts/install_trilingual_models.sh
./scripts/setup.sh
uv run lightrag-server
```

#### 2. 测试 API

**自动化测试**:
```bash
uv run python examples/test_server_trilingual.py
```

**手动测试 (curl)**:
```bash
# 健康检查
curl http://localhost:9621/health

# 中文实体提取
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"腾讯在深圳","language":"zh","mode":"entity_extraction"}'

# 英文实体提取
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Google in California","language":"en","mode":"entity_extraction"}'

# 瑞典语实体提取
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Volvo i Göteborg","language":"sv","mode":"entity_extraction"}'
```

**完整文档**: [docs/ServerTesting-zh.md](docs/ServerTesting-zh.md)

---

### 选项 B: 独立脚本测试（推荐用于开发和学习）

#### 1. 安装依赖和模型

```bash
uv sync --extra trilingual
./scripts/install_trilingual_models.sh
```

#### 2. 运行示例

```bash
# 基础示例（最简单）
uv run python examples/trilingual_extractor_demo.py

# LightRAG 集成示例
uv run python examples/lightrag_with_trilingual.py

# 完整测试套件
uv run python scripts/test_trilingual_extractor.py
```

**完整文档**: [docs/TrilingualNER-Testing-zh.md](docs/TrilingualNER-Testing-zh.md)

---

## 🚀 一键测试（复制粘贴）

### 服务器测试

```bash
cd /home/user/LightRAG && \
./scripts/start_server_with_trilingual.sh &
sleep 10 && \
uv run python examples/test_server_trilingual.py
```

### 脚本测试

```bash
cd /home/user/LightRAG && \
uv sync --extra trilingual && \
./scripts/install_trilingual_models.sh && \
uv run python examples/trilingual_extractor_demo.py
```

---

## 📊 测试对比

| 测试方式 | 适用场景 | 复杂度 | 时间 |
|---------|---------|--------|------|
| 服务器测试 | 生产环境、API 集成 | 中等 | ~10 分钟 |
| 独立脚本测试 | 开发、学习、调试 | 简单 | ~5 分钟 |
| 完整测试套件 | CI/CD、质量保证 | 高 | ~15 分钟 |

---

## 🎯 快速验证（30 秒）

最快验证三语言提取器工作：

```bash
# 启动 Python
uv run python

# 运行以下代码
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

extractor = TrilingualEntityExtractor()
entities = extractor.extract("腾讯在深圳", language="zh")
print([e['entity'] for e in entities])
# 输出: ['腾讯', '深圳']
```

---

## 📚 完整文档

| 文档 | 用途 |
|------|------|
| [ServerTesting-zh.md](docs/ServerTesting-zh.md) | 服务器测试完整指南 |
| [TrilingualNER-Testing-zh.md](docs/TrilingualNER-Testing-zh.md) | 独立脚本测试指南 |
| [TrilingualNER-Usage-zh.md](docs/TrilingualNER-Usage-zh.md) | 使用手册 |
| [UVQuickStart-zh.md](docs/UVQuickStart-zh.md) | UV 包管理器指南 |
| [ConfigurationGuide-zh.md](docs/ConfigurationGuide-zh.md) | 配置系统指南 |

---

## ❓ 常见问题

### Q: 服务器启动失败？
A: 运行 `./scripts/start_server_with_trilingual.sh`，它会自动检查并安装所有依赖。

### Q: 模型下载慢？
A: 首次运行会下载 ~1.4 GB 模型，后续运行很快。可以使用代理或镜像源。

### Q: 如何测试自己的文本？
A: 修改 `examples/test_server_trilingual.py` 或创建自己的测试脚本。

### Q: 支持其他语言吗？
A: 当前支持中文、英文、瑞典语。扩展其他语言参考文档。

---

## 🎉 开始测试

选择一种方式开始：

**生产环境（服务器）**:
```bash
./scripts/start_server_with_trilingual.sh
```

**开发环境（脚本）**:
```bash
uv run python examples/trilingual_extractor_demo.py
```

**快速验证**:
```bash
uv run python -c "
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor
extractor = TrilingualEntityExtractor()
print(extractor.extract('腾讯在深圳', language='zh'))
"
```

---

**祝测试顺利！** 🚀

如有问题，查看完整文档或提交 Issue。
