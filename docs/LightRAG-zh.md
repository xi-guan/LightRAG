# LightRAG 三语言实体提取 - 快速测试

## 目标

用三语言方式启动 LightRAG，手动上传 txt 文件，对比速度和质量。

---

## 步骤

### 1. 安装依赖

```bash
uv sync --extra trilingual --extra api
./scripts/install_trilingual_models.sh
```

### 2. 启用三语言配置

```bash
# 生成配置文件
./scripts/setup.sh

# 编辑 config/local.yaml，添加：
vim config/local.yaml
```

添加以下内容：
```yaml
lightrag:
  entity_extraction:
    use_trilingual: true
    default_language: "zh"
```

```bash
# 重新生成 .env
./scripts/setup.sh
```

### 3. 验证配置

```bash
cat .env | grep USE_TRILINGUAL
# 应该看到: LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL=true
```

### 4. 启动服务器

```bash
uv run lightrag-server
```

### 5. 上传文件测试

新开终端：

```bash
# 上传你的 txt 文件
curl -X POST http://localhost:9621/documents \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$(cat your_file.txt)\",
    \"language\": \"zh\",
    \"use_trilingual\": true
  }"
```

响应会显示：
- 处理时间
- 提取的实体数量
- 实体列表

### 6. 对比测试（可选）

对比 LLM 方式：

```bash
curl -X POST http://localhost:9621/documents \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"$(cat your_file.txt)\",
    \"language\": \"zh\",
    \"use_trilingual\": false
  }"
```

---

## 预期结果

| 指标 | 三语言 | LLM |
|------|--------|-----|
| 速度 | ~1秒 | ~10秒 |
| 实体数量 | 相近或更多 | 基准 |

---

## 如果出错

**配置没生效:**
```bash
./scripts/setup.sh  # 重新生成 .env
# 重启服务器
```

**模型未安装:**
```bash
./scripts/install_trilingual_models.sh
```

**依赖缺失:**
```bash
uv sync --extra trilingual
```
