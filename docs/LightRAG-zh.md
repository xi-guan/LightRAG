# LightRAG 使用指南

## 快速开始

### 安装

```bash
# 1. 安装 UV
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 安装依赖
uv sync --extra trilingual --extra api

# 3. 下载模型
./scripts/install_trilingual_models.sh

# 4. 初始化配置
./scripts/setup.sh

# 5. 启动服务
uv run lightrag-server
```

### 测试

```bash
# 基础测试
uv run python scripts/test_trilingual_extractor.py

# 服务器测试
curl http://localhost:9621/health

# 速度对比
uv run python examples/benchmark_indexing_speed.py
```

---

## 配置

### 配置工作流 (3步启用三语言)

```bash
# 1. 生成配置
./scripts/setup.sh

# 2. 编辑 config/local.yaml
vim config/local.yaml

# 3. 重新生成 .env
./scripts/setup.sh
```

### 配置文件层次

```
config.schema.yaml  → 配置模板(Git追踪, ❌不要编辑)
      ↓
local.yaml          → 你的配置(✅编辑这个)
      ↓
.env                → 环境变量(❌不要编辑, 自动生成)
```

### 最小配置

```yaml
# config/local.yaml
lightrag:
  entity_extraction:
    use_trilingual: true
```

### 完整配置

```yaml
# config/local.yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: "zh"
    fallback_to_llm: true
    auto_detect_language: true
    max_gleaning: 0  # 禁用gleaning提速

trilingual:
  enabled: true
  default_language: "zh"
  lazy_loading: true
  chinese:
    enabled: true
  english:
    enabled: true
    batch_size: 32
  swedish:
    enabled: true
    batch_size: 32
```

### 配置场景

**纯中文文档:**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: "zh"
    max_gleaning: 0
```

**混合语言:**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    auto_detect_language: true
    fallback_to_llm: true
```

**追求最高质量(慢):**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: false
    max_gleaning: 1
```

---

## API 使用

### 实体提取

```bash
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。",
    "language": "zh"
  }'
```

### 文档插入

```bash
curl -X POST http://localhost:9621/documents \
  -H "Content-Type: application/json" \
  -d '{
    "text": "比亚迪是中国最大的电动车制造商之一。",
    "language": "zh",
    "use_trilingual": true
  }'
```

### 查询

```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "比亚迪总部在哪里？",
    "language": "zh"
  }'
```

---

## 性能

### 速度对比

| 提取方式 | 1417文档 | 单块速度 | 提升 |
|---------|----------|----------|------|
| LLM | 5.7小时 | 0.1块/秒 | 1x |
| 三语言 | 0.5-0.8小时 | 0.8块/秒 | 8-15x |

### 质量对比

| 语言 | spaCy/HanLP | GLiNER | 差距 |
|------|-------------|--------|------|
| 中文 | 95% | 24% | -71% |
| 英文 | 90% | 60% | -30% |
| 瑞典语 | 85% | 50% | -35% |

### 优化建议

1. 批量插入代替逐个插入
2. 并发请求 (ThreadPoolExecutor)
3. GPU加速 (pip install spacy[cuda12x])
4. 增加批处理大小 (batch_size: 64)

---

## UV 包管理

### 为什么用 UV

- 速度: 比pip快10-100倍
- 可靠: 自动生成锁文件
- 简单: 命令与pip几乎相同

### 常用命令

```bash
# 安装依赖
uv sync
uv sync --extra trilingual

# 添加依赖
uv add numpy pandas

# 运行脚本
uv run python script.py
uv run lightrag-server

# 更新依赖
uv sync --upgrade
```

---

## 故障排查

### 配置相关

**问题: 修改local.yaml后没生效**
```bash
# 忘记重新生成.env
./scripts/setup.sh
# 然后重启服务器
```

**问题: 找不到local.yaml**
```bash
# 首次运行会生成
./scripts/setup.sh
```

**问题: .env被手动修改后又被覆盖**
```bash
# 不要编辑.env, 编辑local.yaml
vim config/local.yaml
./scripts/setup.sh
```

**问题: 验证配置**
```bash
cat .env | grep TRILINGUAL
# 应看到: LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL=true
```

### 依赖相关

**问题: 模型未找到**
```bash
./scripts/install_trilingual_models.sh
```

**问题: 依赖未安装**
```bash
uv sync --extra trilingual

# 或一键安装
./scripts/start_server_with_trilingual.sh
```

**问题: 导入失败**
```
Failed to import trilingual entity extractor
```
解决: 确保安装了三语言依赖
```bash
uv sync --extra trilingual
./scripts/install_trilingual_models.sh
```

### 性能相关

**问题: 速度提升不明显**
```bash
# 检查配置
cat .env | grep LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL
# 应返回: LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL=true
```

**问题: 内存不足**
```bash
# 使用更小的模型
python -m spacy download en_core_web_sm
python -m spacy download sv_core_news_sm
```

**问题: 首次请求慢**
```bash
# 模型懒加载,首次2-3秒。预热:
curl -X POST http://localhost:9621/extract \
  -d '{"text":"test","language":"zh"}'
```

---

## 配置参考

### 三语言配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| trilingual.enabled | true | 启用三语言提取 |
| trilingual.default_language | en | 默认语言(zh/en/sv) |
| trilingual.lazy_loading | true | 延迟加载(节省内存) |
| trilingual.chinese.model | ELECTRA_BASE_ZH | HanLP模型 |
| trilingual.english.model | en_core_web_trf | spaCy英文模型 |
| trilingual.swedish.model | sv_core_news_lg | spaCy瑞典语模型 |

### LightRAG 配置

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| lightrag.api.host | 0.0.0.0 | API地址 |
| lightrag.api.port | 9621 | API端口 |
| lightrag.llm.provider | openai | LLM提供商 |
| lightrag.llm.model | gpt-4o-mini | LLM模型 |
| lightrag.entity_extraction.use_trilingual | false | 使用三语言提取 |

---

## 支持的实体类型

### 中文 (HanLP)
PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, PERCENT, PRODUCT, EVENT (18种)

### 英文 (spaCy)
PERSON, ORG, GPE, LOC, DATE, TIME, MONEY, PERCENT, PRODUCT, WORK_OF_ART (18种)

### 瑞典语 (spaCy)
PER, ORG, LOC, MISC (4种)

---

## 资源占用

### 磁盘空间
- spaCy英文: 440 MB
- spaCy瑞典语: 545 MB
- HanLP中文: 400 MB
- 总计: 1.4 GB

### 内存占用
- 单语言: 1.5-1.8 GB
- 同时三语言: 4.5 GB (不推荐)

推荐: 按需加载,处理完卸载

---

## Python API

### 基础使用

```python
from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

extractor = TrilingualEntityExtractor()

# 提取中文
entities = extractor.extract("腾讯公司由马化腾创立", language='zh')

# 提取英文
entities = extractor.extract("Apple Inc. founded by Steve Jobs", language='en')

# 提取瑞典语
entities = extractor.extract("Volvo grundades av Assar Gabrielsson", language='sv')
```

### 集成 LightRAG

```python
from lightrag import LightRAG

rag = LightRAG(
    working_dir="./rag_storage",
    use_trilingual=True,
    fallback_to_llm=True
)

rag.insert("腾讯公司由马化腾创立于1998年")
```

---

## 测试清单

- [ ] UV安装成功
- [ ] 依赖安装完成
- [ ] 语言模型下载完成
- [ ] 配置初始化完成
- [ ] 三语言提取测试通过
- [ ] 服务器启动成功
- [ ] API测试通过
- [ ] 速度对比验证

---

## 命令速查

```bash
# 完整安装
curl -LsSf https://astral.sh/uv/install.sh | sh && \
uv sync --extra trilingual --extra api && \
./scripts/install_trilingual_models.sh && \
./scripts/setup.sh

# 启动服务
uv run lightrag-server

# 测试
uv run python scripts/test_trilingual_extractor.py
uv run python examples/benchmark_indexing_speed.py

# 修改配置
nano config/local.yaml && ./scripts/setup.sh

# 健康检查
curl http://localhost:9621/health
```
