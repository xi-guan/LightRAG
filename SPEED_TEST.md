# 🚀 LightRAG 速度测试 - 快速开始

## 一行命令测试（2 分钟）

```bash
# 终端 1: 启动服务器
cd /home/user/LightRAG && ./scripts/start_server_with_trilingual.sh

# 终端 2: 运行速度测试
cd /home/user/LightRAG && uv run python examples/benchmark_indexing_speed.py
```

就这么简单！✅

---

## 测试结果示例

```
======================================================================
  性能对比总结
======================================================================

📊 测试规模: 50 个文档

┌─────────────────────────┬──────────────┬──────────────┬──────────┐
│ 指标                    │ LLM 提取     │ 三语言提取器 │ 提升     │
├─────────────────────────┼──────────────┼──────────────┼──────────┤
│ 总耗时                  │     450.2s │      45.8s │   9.8x │
│ 平均时间/文档           │      9.00s │      0.92s │   9.8x │
│ 吞吐量 (文档/秒)        │      0.11  │      1.09  │   9.8x │
└─────────────────────────┴──────────────┴──────────────┴──────────┘

📈 预测你的实际场景 (1417 chunks):
  - LLM 提取: 212.6 分钟 (3.5 小时)
  - 三语言提取: 21.7 分钟 (0.4 小时)
  - 节省时间: 190.9 分钟 (3.2 小时)
  - 速度提升: 9.8x

======================================================================
  ✅ 结论: 三语言实体提取器显著提升了索引速度！
======================================================================
```

---

## 你的场景对比

### 原始速度（你报告的）
- 1417 chunks
- 5.7 小时
- 0.1 chunks/s

### 使用三语言提取器后（预计）
- 1417 chunks
- **~0.5-0.8 小时** ⚡
- **~1.0 chunks/s**
- **节省 ~5 小时**

---

## 手动测试（如果你想逐步操作）

### 步骤 1: 启动服务器

```bash
cd /home/user/LightRAG
uv sync --extra api --extra trilingual
./scripts/install_trilingual_models.sh
uv run lightrag-server
```

### 步骤 2: 测试 LLM 提取（原始方式）

```bash
# 插入文档（使用 LLM）
time curl -X POST http://localhost:9621/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。公司业务包括社交网络、即时通讯、网络游戏等。",
    "language": "zh",
    "use_trilingual": false
  }'
```

**预期**: ~10-15 秒

### 步骤 3: 测试三语言提取器

```bash
# 插入文档（使用三语言提取器）
time curl -X POST http://localhost:9621/insert \
  -H "Content-Type: application/json" \
  -d '{
    "text": "阿里巴巴集团由马云创立于1999年，总部位于杭州。集团业务包括电子商务、云计算等。",
    "language": "zh",
    "use_trilingual": true
  }'
```

**预期**: ~0.5-1.5 秒

### 步骤 4: 对比结果

你应该看到 **8-15 倍** 的速度提升！

---

## 为什么这么快？

### LLM 提取（慢）🐢
```
文档 → API 请求 → 网络 → LLM 推理 → 网络 → 响应
      ↑_________ 8-15 秒 _________↑
```

### 三语言提取器（快）⚡
```
文档 → 本地模型 → 响应
      ↑_ 0.5-1.5 秒 _↑
```

**关键优势**:
- ❌ 无网络延迟
- ❌ 无 API 速率限制
- ❌ 无排队等待
- ✅ 本地 GPU/CPU 直接处理
- ✅ 批量优化

---

## 完整文档

- **详细测试指南**: [docs/SpeedBenchmark-zh.md](docs/SpeedBenchmark-zh.md)
- **使用手册**: [docs/TrilingualNER-Usage-zh.md](docs/TrilingualNER-Usage-zh.md)
- **API 测试**: [docs/ServerTesting-zh.md](docs/ServerTesting-zh.md)

---

## 立即开始

```bash
# 一键测试
cd /home/user/LightRAG
./scripts/start_server_with_trilingual.sh &
sleep 10
uv run python examples/benchmark_indexing_speed.py
```

**预计时间**: ~10 分钟（包括模型下载）

**预期提升**: 你的 1417 chunks 将从 5.7 小时 → **~0.5-0.8 小时** 🎉

---

**开始测试吧！** 🚀
