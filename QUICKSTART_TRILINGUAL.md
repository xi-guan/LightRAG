# 三语言实体提取器快速开始

## 3 步启用三语言提取器（8-15 倍速度提升）

### 步骤 1：生成初始配置

```bash
./scripts/setup.sh
```

这会生成：
- `config/local.yaml` - 本地配置文件（可编辑）
- `.env` - 环境变量文件（自动生成，不要手动编辑）

### 步骤 2：编辑 config/local.yaml

打开 `config/local.yaml` 并修改以下配置：

```yaml
lightrag:
  entity_extraction:
    use_trilingual: true          # 启用三语言提取器
    default_language: "zh"         # 默认语言（zh/en/sv）
    fallback_to_llm: true          # 失败时回退到 LLM
    auto_detect_language: true     # 自动检测语言
```

### 步骤 3：更新 .env 并启动服务器

```bash
# 重新运行 setup.sh 从 local.yaml 生成 .env
./scripts/setup.sh

# 启动服务器（会自动安装依赖和模型）
./scripts/start_server_with_trilingual.sh
```

## 🎯 配置示例

### 最小配置（启用三语言）

编辑 `config/local.yaml`：

```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
```

然后运行：
```bash
./scripts/setup.sh  # 更新 .env
```

### 完整配置（所有选项）

```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: "zh"
    fallback_to_llm: true
    auto_detect_language: true
    max_gleaning: 0  # 使用三语言时建议禁用 gleaning

trilingual:
  enabled: true
  default_language: "zh"
  lazy_loading: true

  # 中文配置
  chinese:
    enabled: true
    model: "CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH"

  # 英文配置
  english:
    enabled: true
    model: "en_core_web_trf"
    batch_size: 32

  # 瑞典语配置
  swedish:
    enabled: true
    model: "sv_core_news_lg"
    batch_size: 32
```

## 📋 完整工作流程

```bash
# 1. 初次设置 - 生成配置文件
./scripts/setup.sh
# 输出：
#   - config/local.yaml ✓
#   - .env ✓

# 2. 编辑配置
nano config/local.yaml
# 或
vim config/local.yaml
# 或使用任何编辑器

# 3. 更新环境变量
./scripts/setup.sh  # 从 local.yaml 重新生成 .env

# 4. 安装依赖和模型（如果还没安装）
uv sync --extra trilingual
./scripts/install_trilingual_models.sh

# 5. 启动服务器
uv run lightrag-server --host 0.0.0.0 --port 9621

# 或使用一键启动脚本（自动完成 4-5 步）
./scripts/start_server_with_trilingual.sh
```

## 🔄 修改配置后的流程

```bash
# 1. 编辑配置
vim config/local.yaml

# 2. 更新 .env
./scripts/setup.sh

# 3. 重启服务器
# 按 Ctrl+C 停止服务器，然后重新启动
uv run lightrag-server --host 0.0.0.0 --port 9621
```

## 📁 配置文件说明

| 文件 | 用途 | 是否编辑 |
|------|------|----------|
| `config/config.schema.yaml` | 配置模板（定义所有可用选项） | ❌ 不要编辑 |
| `config/local.yaml` | **你的配置文件** | ✅ **编辑这个** |
| `.env` | 环境变量（从 local.yaml 自动生成） | ❌ 不要编辑 |

## 🚀 验证配置

### 检查生成的 .env

```bash
cat .env | grep TRILINGUAL
```

应该看到：
```bash
# LIGHTRAG
LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL=true
LIGHTRAG_ENTITY_EXTRACTION_DEFAULT_LANGUAGE=zh
LIGHTRAG_ENTITY_EXTRACTION_FALLBACK_TO_LLM=true
LIGHTRAG_ENTITY_EXTRACTION_AUTO_DETECT_LANGUAGE=true

# TRILINGUAL
TRILINGUAL_ENABLED=true
TRILINGUAL_DEFAULT_LANGUAGE=zh
...
```

### 检查服务器日志

启动服务器后，应该看到：
```
INFO: Trilingual entity extractor initialized successfully
INFO:   - Fallback to LLM: True
INFO:   - Default language: zh
```

## 🧪 测试

### 快速测试

```bash
# 启动服务器
./scripts/start_server_with_trilingual.sh

# 在另一个终端测试
curl -X POST http://localhost:9621/documents/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。"
  }'
```

### 交互式测试

```bash
uv run python examples/upload_and_test.py
```

### 速度对比测试

```bash
uv run python examples/benchmark_indexing_speed.py
```

## 💡 提示

### 1. 配置优先级

即使在 `config/local.yaml` 中设置了配置，API 请求仍然可以覆盖：

```bash
curl -X POST http://localhost:9621/documents/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "...",
    "use_trilingual": false  # 覆盖全局配置，这次使用 LLM
  }'
```

### 2. 推荐配置

**处理纯中文文档：**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: "zh"
    max_gleaning: 0  # 禁用 gleaning 提升速度
```

**处理混合语言文档：**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    auto_detect_language: true
    fallback_to_llm: true  # 对于不支持的语言回退到 LLM
```

**追求最高质量（慢）：**
```yaml
lightrag:
  entity_extraction:
    use_trilingual: false  # 完全使用 LLM
    max_gleaning: 1
```

### 3. 性能对比

| 配置 | 速度 | 质量 | 使用场景 |
|------|------|------|----------|
| `use_trilingual: true, max_gleaning: 0` | ⚡⚡⚡ 最快 | ⭐⭐⭐ 高 | 大批量文档 |
| `use_trilingual: true, max_gleaning: 1` | ⚡⚡ 较快 | ⭐⭐⭐⭐ 很高 | 平衡速度和质量 |
| `use_trilingual: false, max_gleaning: 1` | ⚡ 慢 | ⭐⭐⭐⭐⭐ 最高 | 重要文档 |

## 🔧 故障排查

### 问题 1：修改 local.yaml 后没有生效

**原因**：忘记重新运行 `setup.sh`

**解决**：
```bash
./scripts/setup.sh  # 从 local.yaml 重新生成 .env
# 然后重启服务器
```

### 问题 2：找不到 local.yaml

**原因**：还没运行过 `setup.sh`

**解决**：
```bash
./scripts/setup.sh  # 首次运行会生成 local.yaml
```

### 问题 3：.env 被手动修改后又被覆盖

**原因**：`.env` 是自动生成的，每次运行 `setup.sh` 都会重新生成

**解决**：
```bash
# 不要直接编辑 .env，而是编辑 local.yaml
vim config/local.yaml
./scripts/setup.sh  # 重新生成 .env
```

### 问题 4：模型未安装

**错误信息**：
```
Failed to import trilingual entity extractor
```

**解决**：
```bash
# 安装依赖
uv sync --extra trilingual

# 下载模型
./scripts/install_trilingual_models.sh

# 或使用一键脚本（自动完成所有步骤）
./scripts/start_server_with_trilingual.sh
```

## 📚 相关文档

- [完整配置指南](./docs/TrilingualConfiguration-zh.md)
- [三语言提取器使用指南](./docs/TrilingualNER-Usage-zh.md)
- [性能测试指南](./docs/SpeedBenchmark-zh.md)
- [实际测试指南](./REALWORLD_TEST.md)

## 🎯 总结

配置三语言提取器只需 3 步：

```bash
# 1. 生成配置
./scripts/setup.sh

# 2. 编辑配置
vim config/local.yaml  # 设置 use_trilingual: true

# 3. 更新并启动
./scripts/setup.sh
./scripts/start_server_with_trilingual.sh
```

**记住：编辑 `config/local.yaml`，而不是 `.env`！**
