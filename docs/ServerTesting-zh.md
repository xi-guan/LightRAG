# LightRAG Server 三语言实体提取器测试指南

## 快速开始（5 分钟）

### 步骤 1: 安装依赖

```bash
cd /home/user/LightRAG

# 安装 API 服务器 + 三语言支持
uv sync --extra api --extra trilingual
```

### 步骤 2: 下载语言模型

```bash
./scripts/install_trilingual_models.sh
```

### 步骤 3: 初始化配置

```bash
./scripts/setup.sh
```

### 步骤 4: 启动服务器

```bash
# 方式 1: 使用 UV (推荐)
uv run lightrag-server

# 方式 2: 使用 Python
python -m lightrag.api.lightrag_server

# 方式 3: 生产环境 (Gunicorn)
uv run lightrag-gunicorn
```

**预期输出**:
```
INFO:     Started server process
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:9621
```

### 步骤 5: 测试服务器

**新开一个终端**，运行测试脚本：

```bash
# 自动化测试
uv run python examples/test_server_trilingual.py

# 或指定服务器地址
uv run python examples/test_server_trilingual.py http://localhost:9621
```

---

## 手动 API 测试

### 测试 1: 健康检查

```bash
curl http://localhost:9621/health
```

**预期响应**:
```json
{
  "status": "healthy",
  "version": "1.0.0",
  "trilingual_enabled": true
}
```

---

### 测试 2: 中文实体提取

```bash
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。",
    "language": "zh",
    "mode": "entity_extraction"
  }'
```

**预期响应**:
```json
{
  "entities": [
    {
      "entity": "腾讯公司",
      "type": "ORG",
      "start": 0,
      "end": 4
    },
    {
      "entity": "马化腾",
      "type": "PERSON",
      "start": 5,
      "end": 8
    },
    {
      "entity": "1998年",
      "type": "DATE",
      "start": 11,
      "end": 16
    },
    {
      "entity": "深圳",
      "type": "GPE",
      "start": 20,
      "end": 22
    }
  ],
  "language": "zh",
  "processing_time": 0.15
}
```

---

### 测试 3: 英文实体提取

```bash
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Microsoft was founded by Bill Gates in Seattle.",
    "language": "en",
    "mode": "entity_extraction"
  }'
```

**预期响应**:
```json
{
  "entities": [
    {
      "entity": "Microsoft",
      "type": "ORG",
      "start": 0,
      "end": 9
    },
    {
      "entity": "Bill Gates",
      "type": "PERSON",
      "start": 25,
      "end": 35
    },
    {
      "entity": "Seattle",
      "type": "GPE",
      "start": 39,
      "end": 46
    }
  ],
  "language": "en",
  "processing_time": 0.12
}
```

---

### 测试 4: 瑞典语实体提取

```bash
curl -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Spotify grundades av Daniel Ek i Stockholm.",
    "language": "sv",
    "mode": "entity_extraction"
  }'
```

**预期响应**:
```json
{
  "entities": [
    {
      "entity": "Spotify",
      "type": "ORG",
      "start": 0,
      "end": 7
    },
    {
      "entity": "Daniel Ek",
      "type": "PERSON",
      "start": 21,
      "end": 30
    },
    {
      "entity": "Stockholm",
      "type": "GPE",
      "start": 33,
      "end": 42
    }
  ],
  "language": "sv",
  "processing_time": 0.14
}
```

---

### 测试 5: 插入文档

```bash
curl -X POST http://localhost:9621/documents \
  -H "Content-Type: application/json" \
  -d '{
    "text": "比亚迪是中国最大的电动车制造商之一，总部位于深圳。公司成立于1995年。",
    "language": "zh",
    "mode": "insert"
  }'
```

**预期响应**:
```json
{
  "status": "success",
  "document_id": "doc_123456",
  "entities_extracted": 4,
  "processing_time": 0.25
}
```

---

### 测试 6: 查询文档

```bash
curl -X POST http://localhost:9621/query \
  -H "Content-Type: application/json" \
  -d '{
    "query": "比亚迪总部在哪里？",
    "language": "zh",
    "mode": "query"
  }'
```

**预期响应**:
```json
{
  "answer": "比亚迪总部位于深圳。",
  "entities": ["比亚迪", "深圳"],
  "confidence": 0.95,
  "sources": [
    {
      "document_id": "doc_123456",
      "text": "比亚迪是中国最大的电动车制造商之一，总部位于深圳。",
      "relevance": 0.98
    }
  ]
}
```

---

### 测试 7: 批量提取

```bash
curl -X POST http://localhost:9621/batch_extract \
  -H "Content-Type: application/json" \
  -d '{
    "documents": [
      {
        "text": "阿里巴巴集团由马云创立",
        "language": "zh"
      },
      {
        "text": "Amazon was founded by Jeff Bezos",
        "language": "en"
      },
      {
        "text": "Volvo grundades av Assar Gabrielsson",
        "language": "sv"
      }
    ]
  }'
```

**预期响应**:
```json
{
  "results": [
    {
      "entities": [
        {"entity": "阿里巴巴集团", "type": "ORG"},
        {"entity": "马云", "type": "PERSON"}
      ],
      "language": "zh"
    },
    {
      "entities": [
        {"entity": "Amazon", "type": "ORG"},
        {"entity": "Jeff Bezos", "type": "PERSON"}
      ],
      "language": "en"
    },
    {
      "entities": [
        {"entity": "Volvo", "type": "ORG"},
        {"entity": "Assar Gabrielsson", "type": "PERSON"}
      ],
      "language": "sv"
    }
  ],
  "total_processed": 3,
  "total_time": 0.42
}
```

---

## 使用 Python Requests

### 基础示例

```python
import requests

# 服务器地址
BASE_URL = "http://localhost:9621"

# 提取中文实体
response = requests.post(
    f"{BASE_URL}/extract",
    json={
        "text": "华为技术有限公司成立于1987年，创始人任正非。",
        "language": "zh",
        "mode": "entity_extraction"
    }
)

result = response.json()
print(f"提取到 {len(result['entities'])} 个实体:")
for ent in result['entities']:
    print(f"  - {ent['entity']}: {ent['type']}")
```

### 批量处理示例

```python
import requests

BASE_URL = "http://localhost:9621"

documents = [
    {"text": "苹果公司在库比蒂诺", "language": "zh"},
    {"text": "Google in Mountain View", "language": "en"},
    {"text": "Spotify i Stockholm", "language": "sv"},
]

for doc in documents:
    response = requests.post(
        f"{BASE_URL}/extract",
        json={
            "text": doc["text"],
            "language": doc["language"],
            "mode": "entity_extraction"
        }
    )

    result = response.json()
    entities = [e['entity'] for e in result['entities']]
    print(f"{doc['language']}: {entities}")
```

---

## 使用 httpie

更友好的命令行工具（需要安装: `pip install httpie`）

### 中文提取

```bash
http POST localhost:9621/extract \
  text="腾讯公司在深圳" \
  language=zh \
  mode=entity_extraction
```

### 英文提取

```bash
http POST localhost:9621/extract \
  text="Apple Inc. in Cupertino" \
  language=en \
  mode=entity_extraction
```

### 瑞典语提取

```bash
http POST localhost:9621/extract \
  text="Volvo i Göteborg" \
  language=sv \
  mode=entity_extraction
```

---

## 性能测试

### 使用 Apache Bench

```bash
# 安装 ab
sudo apt-get install apache2-utils  # Ubuntu/Debian
brew install httpd  # macOS

# 创建测试数据文件
cat > test_data.json << 'EOF'
{
  "text": "苹果公司由史蒂夫·乔布斯创立",
  "language": "zh",
  "mode": "entity_extraction"
}
EOF

# 运行性能测试 (100 请求，10 并发)
ab -n 100 -c 10 -p test_data.json -T application/json \
  http://localhost:9621/extract
```

**预期输出**:
```
Requests per second:    50.23 [#/sec] (mean)
Time per request:       19.908 [ms] (mean)
Time per request:       1.991 [ms] (mean, across all concurrent requests)
```

### 使用 wrk

```bash
# 安装 wrk
git clone https://github.com/wg/wrk.git
cd wrk && make

# 运行负载测试 (2 线程, 10 连接, 持续 30 秒)
./wrk -t2 -c10 -d30s --script=post.lua http://localhost:9621/extract
```

---

## 自动化测试脚本

### 完整测试流程

```bash
#!/bin/bash
# test_lightrag_server.sh

set -e

echo "========================================="
echo "  LightRAG Server 三语言测试"
echo "========================================="

# 1. 启动服务器（后台）
echo ""
echo "1. 启动服务器..."
uv run lightrag-server &
SERVER_PID=$!

# 等待服务器启动
sleep 5

# 2. 健康检查
echo ""
echo "2. 健康检查..."
curl -s http://localhost:9621/health | jq

# 3. 中文测试
echo ""
echo "3. 测试中文实体提取..."
curl -s -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"腾讯在深圳","language":"zh","mode":"entity_extraction"}' \
  | jq '.entities'

# 4. 英文测试
echo ""
echo "4. 测试英文实体提取..."
curl -s -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Google in California","language":"en","mode":"entity_extraction"}' \
  | jq '.entities'

# 5. 瑞典语测试
echo ""
echo "5. 测试瑞典语实体提取..."
curl -s -X POST http://localhost:9621/extract \
  -H "Content-Type: application/json" \
  -d '{"text":"Volvo i Göteborg","language":"sv","mode":"entity_extraction"}' \
  | jq '.entities'

# 6. 清理
echo ""
echo "6. 停止服务器..."
kill $SERVER_PID

echo ""
echo "========================================="
echo "  ✅ 测试完成"
echo "========================================="
```

运行:
```bash
chmod +x test_lightrag_server.sh
./test_lightrag_server.sh
```

---

## Docker 部署测试

### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# 安装 UV
RUN pip install uv

# 复制项目文件
COPY . .

# 安装依赖
RUN uv sync --extra api --extra trilingual

# 下载模型
RUN ./scripts/install_trilingual_models.sh

# 初始化配置
RUN ./scripts/setup.sh

# 暴露端口
EXPOSE 9621

# 启动服务器
CMD ["uv", "run", "lightrag-server"]
```

### 构建和运行

```bash
# 构建镜像
docker build -t lightrag-trilingual .

# 运行容器
docker run -d -p 9621:9621 --name lightrag lightrag-trilingual

# 测试
curl http://localhost:9621/health

# 停止
docker stop lightrag
```

---

## 监控和日志

### 查看日志

```bash
# 实时日志
uv run lightrag-server --log-level debug

# 保存到文件
uv run lightrag-server > lightrag.log 2>&1 &

# 查看日志
tail -f lightrag.log
```

### Prometheus 监控

在 `lightrag_server.py` 中添加：

```python
from prometheus_client import Counter, Histogram, generate_latest

# 指标
extraction_requests = Counter('extraction_requests_total', 'Total extraction requests', ['language'])
extraction_duration = Histogram('extraction_duration_seconds', 'Extraction duration', ['language'])

@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type="text/plain")
```

访问指标:
```bash
curl http://localhost:9621/metrics
```

---

## 常见问题

### Q1: 服务器启动失败

**症状**:
```
Address already in use
```

**解决**:
```bash
# 查找占用端口的进程
lsof -i :9621

# 杀死进程
kill -9 <PID>

# 或使用其他端口
uv run lightrag-server --port 9622
```

### Q2: 模型加载超时

**症状**:
```
TimeoutError: Model loading timeout
```

**解决**:
```bash
# 增加超时时间
export MODEL_LOAD_TIMEOUT=300

# 或预加载模型
./scripts/install_trilingual_models.sh
```

### Q3: 内存不足

**症状**:
```
MemoryError: Unable to allocate memory
```

**解决**:
- 限制并发请求数
- 使用更小的模型
- 增加系统内存或使用交换空间

### Q4: API 响应慢

**优化建议**:
1. 启用 uvicorn worker 并发
2. 使用 Redis 缓存结果
3. 批量处理请求
4. 使用 GPU 加速

---

## API 参考

### POST /extract

提取文本中的实体

**请求**:
```json
{
  "text": "文本内容",
  "language": "zh|en|sv",
  "mode": "entity_extraction"
}
```

**响应**:
```json
{
  "entities": [
    {
      "entity": "实体文本",
      "type": "ORG|PERSON|GPE|LOC|DATE",
      "start": 0,
      "end": 10
    }
  ],
  "language": "zh",
  "processing_time": 0.15
}
```

### POST /documents

插入文档

**请求**:
```json
{
  "text": "文档内容",
  "language": "zh|en|sv",
  "mode": "insert"
}
```

**响应**:
```json
{
  "status": "success",
  "document_id": "doc_123456",
  "entities_extracted": 5
}
```

### POST /query

查询文档

**请求**:
```json
{
  "query": "查询问题",
  "language": "zh|en|sv",
  "mode": "query"
}
```

**响应**:
```json
{
  "answer": "答案",
  "entities": ["实体1", "实体2"],
  "confidence": 0.95
}
```

---

## 下一步

- **生产部署**: 参考 [部署指南](./Deployment-zh.md)
- **性能优化**: 参考 [优化指南](./TrilingualNER-Usage-zh.md#性能优化)
- **监控告警**: 配置 Prometheus + Grafana

---

**祝测试顺利！** 🚀
