# 三语言实体提取器配置指南

## 简介

LightRAG 现在支持使用专门的 NER（命名实体识别）模型来替代 LLM 进行实体提取，大幅提升速度（**8-15 倍**）。

## 配置方式

### 方式 1：环境变量（推荐）

在 `.env` 文件中添加以下配置：

```bash
# 启用三语言实体提取器
USE_TRILINGUAL_EXTRACTOR=true

# 默认语言（zh/en/sv）
TRILINGUAL_DEFAULT_LANGUAGE=zh

# 当提取失败时是否回退到 LLM
TRILINGUAL_FALLBACK_TO_LLM=true

# 是否自动检测语言
TRILINGUAL_AUTO_DETECT_LANGUAGE=true
```

### 方式 2：config/local.yaml

```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: zh
    fallback_to_llm: true
    auto_detect_language: true
```

### 方式 3：API 请求参数（每次请求控制）

```bash
# 使用三语言提取器处理中文文档
curl -X POST http://localhost:9621/documents/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。",
    "language": "zh",
    "use_trilingual": true
  }'

# 使用 LLM 提取（覆盖全局配置）
curl -X POST http://localhost:9621/documents/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Some text...",
    "use_trilingual": false
  }'
```

## 配置参数说明

| 参数 | 类型 | 默认值 | 说明 |
|------|------|--------|------|
| `USE_TRILINGUAL_EXTRACTOR` | boolean | false | 是否启用三语言提取器 |
| `TRILINGUAL_DEFAULT_LANGUAGE` | string | "en" | 默认语言（zh/en/sv） |
| `TRILINGUAL_FALLBACK_TO_LLM` | boolean | true | 失败时是否回退到 LLM |
| `TRILINGUAL_AUTO_DETECT_LANGUAGE` | boolean | true | 是否自动检测语言 |

## 支持的语言

| 语言 | 代码 | 模型 | F1 分数 |
|------|------|------|---------|
| 中文 | zh | HanLP | 95% |
| 英文 | en | spaCy (en_core_web_trf) | 90% |
| 瑞典语 | sv | spaCy (sv_core_news_lg) | 85% |

## 快速开始

### 1. 安装依赖

```bash
# 使用 UV 安装（推荐）
uv sync --extra trilingual

# 或使用 pip
pip install -r requirements-trilingual.txt
```

### 2. 下载语言模型

```bash
./scripts/install_trilingual_models.sh
```

### 3. 启用配置

编辑 `.env` 文件：

```bash
USE_TRILINGUAL_EXTRACTOR=true
```

### 4. 启动服务器

```bash
# 使用一键启动脚本（自动安装+启动）
./scripts/start_server_with_trilingual.sh

# 或手动启动
uv run lightrag-server --host 0.0.0.0 --port 9621
```

### 5. 测试

```bash
# 交互式上传测试
uv run python examples/upload_and_test.py

# 速度对比测试
uv run python examples/benchmark_indexing_speed.py
```

## 配置优先级

**API 请求参数 > 环境变量 > 配置文件 > 默认值**

示例：

```python
# 全局配置：启用三语言
USE_TRILINGUAL_EXTRACTOR=true

# API 请求：覆盖为使用 LLM
{
    "text": "...",
    "use_trilingual": false  # 此次请求使用 LLM
}
```

## 编程方式使用

### Python SDK

```python
from lightrag import LightRAG
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

# 方式 1：使用配置自动初始化
rag = LightRAG(
    working_dir="./rag_storage",
    # 其他配置...
)
# 如果 USE_TRILINGUAL_EXTRACTOR=true，会自动使用三语言提取器

# 方式 2：手动指定提取器
extractor = TrilingualEntityExtractor()
rag = LightRAG(
    working_dir="./rag_storage",
    entity_extractor=extractor,
    use_llm_extraction_fallback=True,
)

# 插入文档
rag.insert("腾讯公司由马化腾创立于1998年")
```

### 自定义提取器

```python
class CustomExtractor:
    def extract(self, text: str, language: str):
        """
        自定义实体提取器

        Args:
            text: 输入文本
            language: 语言代码

        Returns:
            List[{"entity": str, "type": str}]
        """
        # 你的提取逻辑
        return [
            {"entity": "Example", "type": "ORG"}
        ]

# 使用自定义提取器
rag = LightRAG(
    working_dir="./rag_storage",
    entity_extractor=CustomExtractor(),
)
```

## 性能对比

| 提取方式 | 1417 个文档块 | 单块速度 | 相对速度 |
|----------|---------------|----------|----------|
| LLM（GPT-4o-mini） | 5.7 小时 | 0.1 块/秒 | 1x |
| LLM（自托管 Qwen） | ~10+ 小时 | 0.04 块/秒 | 0.4x |
| 三语言提取器 | 0.5-0.8 小时 | 0.8 块/秒 | **8-15x** |

## 故障排查

### 问题 1：模型未找到

```
Error: Model 'en_core_web_trf' not found
```

**解决方案：**
```bash
./scripts/install_trilingual_models.sh
```

### 问题 2：依赖未安装

```
ImportError: No module named 'hanlp'
```

**解决方案：**
```bash
uv sync --extra trilingual
```

### 问题 3：提取器失败但未回退

**解决方案：**

确保启用了回退选项：
```bash
TRILINGUAL_FALLBACK_TO_LLM=true
```

### 问题 4：语言检测不准确

**解决方案：**

手动指定语言：
```python
rag.insert("text...", language="zh")
```

或在 API 请求中：
```json
{
    "text": "...",
    "language": "zh"
}
```

## 最佳实践

### 1. 选择正确的提取方式

| 场景 | 推荐方式 |
|------|----------|
| 纯中文/英文/瑞典语 | 三语言提取器 |
| 混合多语言文档 | LLM |
| 需要提取复杂关系 | LLM |
| 大批量文档处理 | 三语言提取器 |
| 需要自定义实体类型 | LLM |

### 2. 混合使用策略

```python
# 对于重要文档使用 LLM
important_docs = ["doc1.txt", "doc2.txt"]

for doc in documents:
    use_trilingual = doc not in important_docs
    rag.insert(doc, use_trilingual=use_trilingual)
```

### 3. 批量处理优化

```python
# 批量处理相同语言的文档
zh_docs = [...]
en_docs = [...]

for doc in zh_docs:
    rag.insert(doc, language="zh")

for doc in en_docs:
    rag.insert(doc, language="en")
```

## 相关文档

- [三语言提取器使用指南](./TrilingualNER-Usage-zh.md)
- [速度性能测试指南](./SpeedBenchmark-zh.md)
- [实际测试指南](../REALWORLD_TEST.md)
- [API 文档](./API-zh.md)

## 常见问题

**Q: 三语言提取器会提取关系吗？**

A: 不会。三语言提取器只提取实体，关系提取仍然使用 LLM。

**Q: 可以添加其他语言支持吗？**

A: 可以！参考 `lightrag/kg/trilingual_entity_extractor.py` 添加新的 spaCy 模型。

**Q: 提取质量如何？**

A: 对于标准实体类型（人名、组织、地点），三语言提取器质量很高（F1 85-95%）。对于领域特定实体，LLM 可能更好。

**Q: 可以同时使用两种方式吗？**

A: 可以！设置 `TRILINGUAL_FALLBACK_TO_LLM=true`，当三语言提取器失败时会自动使用 LLM。

## 更新日志

- **2025-01-20**: 添加可配置三语言实体提取器支持
- 支持环境变量、配置文件、API 参数三种配置方式
- 支持回退到 LLM 的灵活策略
- 支持每个请求自定义配置

