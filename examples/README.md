# LightRAG 示例代码

本目录包含 LightRAG 的使用示例，帮助你快速上手。

## 三语言实体提取器示例

### 1. 基础示例 (`trilingual_extractor_demo.py`)

**目的**: 演示三语言实体提取器的基本用法

**运行**:
```bash
uv run python examples/trilingual_extractor_demo.py
```

**包含内容**:
- 中文实体提取示例
- 英文实体提取示例
- 瑞典语实体提取示例
- 混合语言场景演示
- 支持的实体类型说明
- 性能对比数据

**适合**: 第一次使用三语言提取器的用户

---

### 2. LightRAG 集成示例 (`lightrag_with_trilingual.py`)

**目的**: 展示如何将三语言提取器集成到 LightRAG 工作流

**运行**:
```bash
uv run python examples/lightrag_with_trilingual.py
```

**包含内容**:
- 简单实体提取
- 多语言知识图谱构建
- 自动语言检测
- 知识库搜索
- 性能优化提示
- 集成指南

**适合**: 需要在 LightRAG 项目中使用三语言提取器的开发者

---

## 前置要求

### 安装依赖

```bash
# 方法 1: 使用 UV (推荐，超快！)
uv sync --extra trilingual

# 方法 2: 使用 pip
pip install -r requirements-trilingual.txt
```

### 下载模型

```bash
./scripts/install_trilingual_models.sh
```

这会下载:
- 英文模型 (en_core_web_trf): ~440 MB
- 瑞典语模型 (sv_core_news_lg): ~545 MB
- 中文模型 (HanLP): ~400 MB (首次使用时自动下载)

**总计**: ~1.4 GB

---

## 快速开始

### 完整流程（5 分钟）

```bash
# 1. 安装 UV (如果还未安装)
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入项目目录
cd /path/to/LightRAG

# 3. 安装依赖
uv sync --extra trilingual

# 4. 下载模型
./scripts/install_trilingual_models.sh

# 5. 运行基础示例
uv run python examples/trilingual_extractor_demo.py

# 6. 运行集成示例
uv run python examples/lightrag_with_trilingual.py
```

---

## 示例对比

| 示例 | 复杂度 | 运行时间 | 适合场景 |
|------|--------|----------|----------|
| `trilingual_extractor_demo.py` | 简单 | ~30 秒 | 学习基础用法 |
| `lightrag_with_trilingual.py` | 中等 | ~60 秒 | 实际项目集成 |
| `scripts/test_trilingual_extractor.py` | 高级 | ~90 秒 | 完整测试 |

---

## 代码片段

### 最小示例

```python
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

# 创建提取器
extractor = TrilingualEntityExtractor()

# 提取中文实体
entities = extractor.extract("苹果公司在库比蒂诺", language="zh")

# 打印结果
for ent in entities:
    print(f"{ent['entity']}: {ent['type']}")
```

### 多语言示例

```python
# 处理多语言文档
documents = [
    {"text": "华为在深圳", "lang": "zh"},
    {"text": "Google in California", "lang": "en"},
    {"text": "Volvo i Göteborg", "lang": "sv"},
]

extractor = TrilingualEntityExtractor()

for doc in documents:
    entities = extractor.extract(doc["text"], language=doc["lang"])
    print(f"{doc['lang']}: {[e['entity'] for e in entities]}")
```

---

## 性能提示

### 延迟加载

```python
# ✅ 好: 只使用需要的语言
extractor = TrilingualEntityExtractor()
extractor.extract(text, language="zh")  # 只加载中文模型

# ❌ 避免: 不必要地加载所有模型
extractor.spacy_en  # 加载英文模型
extractor.spacy_sv  # 加载瑞典语模型
extractor.hanlp     # 加载中文模型
```

### 批处理

```python
# ✅ 好: 批处理提升性能
texts = ["text1", "text2", "text3", ...]
docs = list(extractor.spacy_en.pipe(texts))

# ❌ 避免: 逐个处理
for text in texts:
    doc = extractor.spacy_en(text)
```

---

## 常见问题

### Q: 模型下载失败怎么办？

A: 手动下载:
```bash
python -m spacy download en_core_web_trf
python -m spacy download sv_core_news_lg
```

### Q: 内存不足怎么办？

A: 使用更小的模型:
```bash
# 英文: 12 MB (vs 440 MB)
python -m spacy download en_core_web_sm

# 瑞典语: 12 MB (vs 545 MB)
python -m spacy download sv_core_news_sm
```

修改代码:
```python
# 使用小模型
import spacy
spacy_en = spacy.load("en_core_web_sm")
```

### Q: 如何添加其他语言？

A: 参考 [TrilingualNER-Usage-zh.md](../docs/TrilingualNER-Usage-zh.md#扩展其他语言)

---

## 更多资源

- **完整文档**: [docs/TrilingualNER-Usage-zh.md](../docs/TrilingualNER-Usage-zh.md)
- **测试指南**: [docs/TrilingualNER-Testing-zh.md](../docs/TrilingualNER-Testing-zh.md)
- **UV 快速入门**: [docs/UVQuickStart-zh.md](../docs/UVQuickStart-zh.md)
- **配置指南**: [docs/ConfigurationGuide-zh.md](../docs/ConfigurationGuide-zh.md)

---

## 反馈

如有问题或建议，请提交 Issue 到 GitHub。

**祝使用愉快！** 🚀
