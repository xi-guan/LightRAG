# 如何确认警告来源

## 方法 1: 查看日志关键信息

在你的运行日志中查找以下关键字：

### ✓ 如果使用了 HanLP：
```
INFO: Loading Chinese HanLP model (CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH)...
INFO: ✓ Chinese model loaded successfully
```
**你的日志有这个** ✓ 说明 HanLP 已加载

### ✓ 查找是否有 fallback 到 LLM：
在日志中搜索:
```bash
grep -i "falling back to LLM" your_log_file.txt
grep -i "Custom extractor found" your_log_file.txt
grep -i "Custom extractor failed" your_log_file.txt
```

**如果看到**:
- `Custom extractor found X entities` → 说明使用了 HanLP
- `falling back to LLM` → 说明 HanLP 失败，用了 LLM
- `Custom extractor failed` → 说明 HanLP 报错

### ✓ 警告的来源判断：

**你的警告**:
```
WARNING: chunk-xxx: LLM output format error; found 5/4 feilds on ENTITY `沐春风` @ `雪松长船`
```

这个警告来自 `lightrag/operate.py:388`

**关键点**:
1. HanLP 提取的实体 **永远是 4 个字段**（代码保证）
2. 警告说发现 5 个字段 → **说明来自 LLM 输出**
3. 可能场景：
   - HanLP 提取后，**LLM gleaning** 步骤补充提取时格式错误
   - HanLP 在某些 chunk 上失败，回退到 LLM

## 方法 2: 启用 DEBUG 日志

在你的代码中设置：
```python
import logging
logging.basicConfig(level=logging.DEBUG)

from lightrag import LightRAG
# ... 你的代码
```

然后查看输出中是否有：
```
DEBUG: Custom extractor found X entities
```

## 方法 3: 检查配置

查看你的 LightRAG 初始化代码：
```python
rag = LightRAG(
    entity_extractor=TrilingualEntityExtractor(),  # ← 是否有这一行？
    use_llm_extraction_fallback=True,  # ← 是否开启了 LLM fallback？
    entity_extract_max_gleaning=1,  # ← gleaning 会调用 LLM 补充提取
)
```

**如果 `entity_extract_max_gleaning > 0`**:
- HanLP 先提取实体
- 然后 LLM 会再运行一次补充提取（gleaning）
- **警告很可能来自 gleaning 步骤的 LLM 输出**

## 结论

根据你的情况，最可能的原因是：

1. ✓ HanLP 正常工作，提取实体
2. ✓ 启用了 `entity_extract_max_gleaning`
3. ⚠️ **LLM 在 gleaning 阶段输出了格式错误**（5个字段而非4个）

**解决方法**:
- 设置 `entity_extract_max_gleaning=0` 禁用 gleaning
- 或者调整 LLM 的 temperature 参数降低随机性
- 或者接受这个警告（不影响 HanLP 提取的实体，只是 LLM 补充的部分被跳过）
