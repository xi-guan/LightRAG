# 三语言实体提取器测试指南

## 快速测试（5 分钟）

### 步骤 1: 安装 UV（如果还未安装）

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

### 步骤 2: 进入项目目录

```bash
cd /home/user/LightRAG
```

### 步骤 3: 安装依赖

```bash
# 安装三语言依赖（超快！）
uv sync --extra trilingual
```

### 步骤 4: 下载语言模型

```bash
# 运行安装脚本下载模型
./scripts/install_trilingual_models.sh
```

这会下载：
- 英文模型: ~440 MB
- 瑞典语模型: ~545 MB
- 中文模型: ~400 MB（首次使用时自动下载）

**总计**: ~1.4 GB

### 步骤 5: 运行测试

```bash
# 方式 1: 运行完整测试套件
uv run python scripts/test_trilingual_extractor.py

# 方式 2: 运行基础示例
uv run python examples/trilingual_extractor_demo.py

# 方式 3: 运行 LightRAG 集成示例
uv run python examples/lightrag_with_trilingual.py
```

---

## 详细测试流程

### 测试 1: 基础功能测试

**目的**: 验证三种语言的实体提取功能

```bash
uv run python scripts/test_trilingual_extractor.py
```

**预期输出**:
```
==================================================
  三语言实体提取器测试
==================================================

🧪 测试 1/12: 中文实体提取 - 基础测试
   输入: 苹果公司由史蒂夫·乔布斯在加利福尼亚州创立。
   ✓ 测试通过 (提取到 3 个实体)
   实体: 苹果公司 (ORG), 史蒂夫·乔布斯 (PERSON), 加利福尼亚州 (GPE)

🧪 测试 2/12: 英文实体提取 - 基础测试
   输入: Apple Inc. was founded by Steve Jobs in California.
   ✓ 测试通过 (提取到 3 个实体)
   实体: Apple Inc. (ORG), Steve Jobs (PERSON), California (GPE)

🧪 测试 3/12: 瑞典语实体提取 - 基础测试
   输入: Volvo grundades av Assar Gabrielsson i Göteborg.
   ✓ 测试通过 (提取到 3 个实体)
   实体: Volvo (ORG), Assar Gabrielsson (PERSON), Göteborg (GPE)

...

==================================================
  ✅ 测试完成: 12/12 通过
==================================================
```

### 测试 2: 使用示例

**目的**: 了解如何在代码中使用

```bash
uv run python examples/trilingual_extractor_demo.py
```

**预期输出**:
```
==================================================
  LightRAG 三语言实体提取器使用示例
==================================================

提示: 首次运行会下载模型，请耐心等待...

============================================================
  中文 (HanLP) 实体提取结果
============================================================

1. 苹果公司
   类型: ORG
   位置: 5-9

2. 史蒂夫·乔布斯
   类型: PERSON
   位置: 10-17

...

============================================================
  ✅ 所有示例运行成功！
============================================================
```

### 测试 3: LightRAG 集成测试

**目的**: 验证与 LightRAG 的集成

```bash
uv run python examples/lightrag_with_trilingual.py
```

**预期输出**:
```
==================================================
  LightRAG 三语言实体提取器 - 实际应用示例
==================================================

============================================================
  示例 1: 简单实体提取
============================================================

输入文本: 腾讯公司在深圳成立，马化腾是创始人。
检测到语言: zh
提取结果: ['腾讯公司', '深圳', '马化腾']

...

============================================================
  示例 2: 多语言知识图谱构建
============================================================

处理文档 1/6...
内容预览: 阿里巴巴集团由马云创立于1999年，总部位于杭州...
提取到 4 个实体:
  - 阿里巴巴集团 (ORG)
  - 马云 (PERSON)
  - 1999年 (DATE)
  - 杭州 (GPE)

...

知识图谱构建完成
总实体数: 24

语言分布:
  - 中文: 8 个实体
  - 英文: 8 个实体
  - 瑞典语: 8 个实体
```

---

## 交互式测试

### 创建测试脚本

创建 `test_my_text.py`:

```python
#!/usr/bin/env python3
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

# 创建提取器
extractor = TrilingualEntityExtractor()

# 测试你自己的文本
texts = {
    "zh": "在这里输入你的中文文本...",
    "en": "Enter your English text here...",
    "sv": "Skriv din svenska text här...",
}

for lang, text in texts.items():
    print(f"\n语言: {lang}")
    print(f"文本: {text}")

    entities = extractor.extract(text, language=lang)

    print("实体:")
    for ent in entities:
        print(f"  - {ent['entity']} ({ent['type']})")
```

运行:
```bash
uv run python test_my_text.py
```

---

## 性能测试

### 速度测试

```bash
# 运行性能测试（包含在完整测试中）
uv run python scripts/test_trilingual_extractor.py

# 查看性能部分
```

**预期结果**:
```
⚡ 性能测试

中文 (HanLP):
  - 处理 10 个文档
  - 平均时间: ~0.15 秒/文档
  - 吞吐量: ~6.7 文档/秒

英文 (spaCy):
  - 处理 10 个文档
  - 平均时间: ~0.12 秒/文档
  - 吞吐量: ~8.3 文档/秒

瑞典语 (spaCy):
  - 处理 10 个文档
  - 平均时间: ~0.14 秒/文档
  - 吞吐量: ~7.1 文档/秒
```

### 内存测试

```python
import psutil
import os
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

# 记录初始内存
process = psutil.Process(os.getpid())
mem_before = process.memory_info().rss / 1024 / 1024  # MB

# 创建提取器（延迟加载，内存占用很小）
extractor = TrilingualEntityExtractor()
mem_after_init = process.memory_info().rss / 1024 / 1024

print(f"初始化后内存增加: {mem_after_init - mem_before:.1f} MB")

# 使用英文模型
extractor.extract("Test", language="en")
mem_after_en = process.memory_info().rss / 1024 / 1024

print(f"英文模型加载后: {mem_after_en - mem_before:.1f} MB")

# 使用中文模型（英文模型仍在内存中）
extractor.extract("测试", language="zh")
mem_after_zh = process.memory_info().rss / 1024 / 1024

print(f"中文模型加载后: {mem_after_zh - mem_before:.1f} MB")
```

**预期输出**:
```
初始化后内存增加: ~2 MB (只是对象创建)
英文模型加载后: ~1600 MB
中文模型加载后: ~3200 MB
```

**注意**: 虽然两个模型都在内存中，但由于延迟加载，你可以选择只使用一种语言来节省内存。

---

## 常见问题排查

### 问题 1: 模型下载失败

**症状**:
```
OSError: [E050] Can't find model 'en_core_web_trf'
```

**解决方法**:
```bash
# 手动下载模型
python -m spacy download en_core_web_trf
python -m spacy download sv_core_news_lg

# 或重新运行安装脚本
./scripts/install_trilingual_models.sh
```

### 问题 2: HanLP 下载超时

**症状**:
```
ConnectionError: HanLP model download timeout
```

**解决方法**:
```python
# 设置代理或镜像源
import hanlp
hanlp.pretrained.mtl.CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH['mirror'] = 'your-mirror-url'
```

或者手动下载模型并放置到 `~/.hanlp/` 目录。

### 问题 3: 依赖冲突

**症状**:
```
ImportError: No module named 'spacy'
```

**解决方法**:
```bash
# 重新安装依赖
uv sync --extra trilingual

# 或使用 pip
pip install -r requirements-trilingual.txt
```

### 问题 4: 内存不足

**症状**:
```
MemoryError: Unable to allocate memory
```

**解决方法**:
- **方案 1**: 一次只使用一种语言
- **方案 2**: 使用更小的模型:
  ```bash
  # 英文: 使用 en_core_web_sm (12 MB) 代替 en_core_web_trf (440 MB)
  python -m spacy download en_core_web_sm

  # 瑞典语: 使用 sv_core_news_sm (12 MB) 代替 sv_core_news_lg (545 MB)
  python -m spacy download sv_core_news_sm
  ```
- **方案 3**: 增加系统交换空间

### 问题 5: GPU 不可用

**症状**:
```
Warning: GPU not available, using CPU
```

**解决方法**（可选，CPU 已足够快）:
```bash
# 安装 GPU 版本的 spaCy
pip install spacy[cuda]  # CUDA 11.x
pip install spacy[cuda12x]  # CUDA 12.x

# 验证 GPU
python -c "import spacy; spacy.prefer_gpu()"
```

---

## 单元测试

### 运行所有测试

```bash
# 使用 pytest
uv run pytest tests/ -v

# 只运行三语言提取器测试
uv run pytest tests/test_trilingual_extractor.py -v
```

### 测试覆盖率

```bash
uv run pytest --cov=lightrag.kg.trilingual_entity_extractor --cov-report=html
```

---

## 性能基准

### 不同模型对比

| 语言 | 工具 | 模型 | F1 分数 | 速度 | 内存 |
|------|------|------|---------|------|------|
| 中文 | HanLP | ELECTRA-base | **95%** | 中等 | ~1.5 GB |
| 中文 | GLiNER | multilingual | 24% | 快 | ~500 MB |
| 英文 | spaCy | en_core_web_trf | **90%** | 中等 | ~1.6 GB |
| 英文 | spaCy | en_core_web_lg | 85% | 快 | ~800 MB |
| 英文 | spaCy | en_core_web_sm | 70% | 很快 | ~12 MB |
| 英文 | GLiNER | multilingual | 60% | 快 | ~500 MB |
| 瑞典语 | spaCy | sv_core_news_lg | **85%** | 中等 | ~1.7 GB |
| 瑞典语 | spaCy | sv_core_news_sm | 65% | 快 | ~12 MB |
| 瑞典语 | GLiNER | multilingual | 50% | 快 | ~500 MB |

**推荐配置**（当前默认）:
- 中文: HanLP ELECTRA-base
- 英文: spaCy en_core_web_trf
- 瑞典语: spaCy sv_core_news_lg

**低资源配置**（如果内存 < 4 GB）:
- 中文: 保持 HanLP（无替代方案）
- 英文: spaCy en_core_web_sm
- 瑞典语: spaCy sv_core_news_sm

---

## 集成测试

### 测试与 LightRAG API 集成

```bash
# 启动 LightRAG 服务器
uv run lightrag-server

# 在另一个终端测试 API
curl -X POST http://localhost:9621/extract_entities \
  -H "Content-Type: application/json" \
  -d '{
    "text": "苹果公司在库比蒂诺",
    "language": "zh"
  }'
```

**预期响应**:
```json
{
  "entities": [
    {"entity": "苹果公司", "type": "ORG", "start": 0, "end": 4},
    {"entity": "库比蒂诺", "type": "GPE", "start": 5, "end": 9}
  ]
}
```

---

## 测试清单

完成以下测试确保系统正常工作：

- [ ] ✅ UV 安装成功
- [ ] ✅ 依赖安装成功 (`uv sync --extra trilingual`)
- [ ] ✅ 英文模型下载成功
- [ ] ✅ 瑞典语模型下载成功
- [ ] ✅ HanLP 中文模型下载成功（首次使用）
- [ ] ✅ 中文实体提取测试通过
- [ ] ✅ 英文实体提取测试通过
- [ ] ✅ 瑞典语实体提取测试通过
- [ ] ✅ 延迟加载测试通过
- [ ] ✅ 性能测试满足要求
- [ ] ✅ 示例脚本运行成功
- [ ] ✅ LightRAG 集成测试通过

---

## 下一步

测试完成后，你可以：

1. **集成到项目**: 参考 [集成指南](./TrilingualNER-Usage-zh.md#集成到-lightrag)
2. **优化性能**: 参考 [性能优化指南](./TrilingualNER-Usage-zh.md#性能优化)
3. **生产部署**: 参考 [部署指南](./TrilingualNER-Usage-zh.md#生产部署)

---

## 获取帮助

- **文档**: [TrilingualNER-Usage-zh.md](./TrilingualNER-Usage-zh.md)
- **UV 指南**: [UVQuickStart-zh.md](./UVQuickStart-zh.md)
- **问题反馈**: GitHub Issues

---

**祝测试顺利！** 🚀
