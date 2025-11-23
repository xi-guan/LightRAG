#!/usr/bin/env python3
"""
调试脚本：验证实体提取来源（HanLP vs LLM）
"""

import logging

# 设置日志级别为 DEBUG
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# 检查 HanLP 是否可用
try:
    import hanlp
    HANLP_AVAILABLE = True
except ImportError:
    HANLP_AVAILABLE = False
    print("警告: HanLP 未安装，跳过 HanLP 测试")

def convert_to_llm_format(entities, tuple_delimiter="<|#|>", completion_delimiter="<|COMPLETE|>"):
    """简化版的转换函数"""
    if not entities:
        return completion_delimiter

    type_mapping = {
        "PERSON": "person", "PER": "person",
        "ORG": "organization", "ORGANIZATION": "organization",
        "GPE": "location", "LOC": "location", "LOCATION": "location",
        "FAC": "location", "FACILITY": "location",
    }

    lines = []
    for ent in entities:
        entity_name = ent.get("entity", "").strip()
        entity_type = ent.get("type", "Other").upper()
        if not entity_name:
            continue
        mapped_type = type_mapping.get(entity_type, "other")
        description = f"{entity_name} is a {mapped_type}"
        line = f"entity{tuple_delimiter}{entity_name}{tuple_delimiter}{mapped_type}{tuple_delimiter}{description}"
        lines.append(line)

    result = "\n".join(lines)
    if result:
        result += f"\n{completion_delimiter}"
    else:
        result = completion_delimiter
    return result


def test_hanlp_extraction():
    """测试 HanLP 提取中文实体"""
    print("\n" + "="*60)
    print("测试 1: HanLP 中文实体提取")
    print("="*60)

    if not HANLP_AVAILABLE:
        print("\n✗ HanLP 未安装，跳过此测试")
        return False

    # 使用你日志中出现的实体
    test_text = """
    沐春风在雪松长船上遇到了萧瑟、雷无桀和唐莲。
    他们一起从三蛇岛航向北离海域。
    唐莲来自雪月城，船舱内的lighting很好。
    """

    print(f"\n测试文本:\n{test_text.strip()}\n")

    try:
        # 直接使用 HanLP
        print("加载 HanLP 模型...")
        model_name = "CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH"
        model_path = getattr(hanlp.pretrained.mtl, model_name, model_name)
        nlp = hanlp.load(model_path)
        print("✓ 模型加载成功\n")

        # 提取实体
        result = nlp(test_text, tasks=["tok", "ner"])

        # 找到 tok 和 ner 的 key
        tok_key = next((k for k in result.keys() if isinstance(k, str) and (k == "tok" or k.startswith("tok/"))), None)
        ner_key = next((k for k in result.keys() if isinstance(k, str) and (k == "ner" or k.startswith("ner/"))), None)

        entities = []
        current_entity = []
        current_type = None
        current_start = 0
        char_position = 0

        for tokens, labels in zip(result[tok_key], result[ner_key]):
            for token, label in zip(tokens, labels):
                if not isinstance(label, str):
                    label = str(label)
                if not isinstance(token, str):
                    token = str(token)

                if label.startswith("B-"):
                    if current_entity:
                        entities.append({
                            "entity": "".join(current_entity),
                            "type": current_type,
                            "score": 1.0,
                            "start": current_start,
                            "end": char_position,
                        })
                    current_entity = [token]
                    current_type = label[2:]
                    current_start = char_position
                elif label.startswith("I-") and current_entity:
                    current_entity.append(token)
                else:
                    if current_entity:
                        entities.append({
                            "entity": "".join(current_entity),
                            "type": current_type,
                            "score": 1.0,
                            "start": current_start,
                            "end": char_position,
                        })
                        current_entity = []
                        current_type = None
                char_position += len(token)

        if current_entity:
            entities.append({
                "entity": "".join(current_entity),
                "type": current_type,
                "score": 1.0,
                "start": current_start,
                "end": char_position,
            })

        print(f"✓ HanLP 成功提取 {len(entities)} 个实体:\n")
        for i, ent in enumerate(entities, 1):
            print(f"  {i}. {ent['entity']:10s} | 类型: {ent['type']:8s} | 位置: {ent['start']}-{ent['end']}")

        # 转换为 LLM 格式
        print("\n" + "-"*60)
        print("转换为 LLM 格式:")
        print("-"*60 + "\n")

        llm_format = convert_to_llm_format(entities)
        print(llm_format)

        # 验证格式
        print("\n" + "-"*60)
        print("格式验证:")
        print("-"*60 + "\n")

        lines = llm_format.strip().split('\n')
        for line in lines:
            if line == "<|COMPLETE|>":
                continue
            fields = line.split("<|#|>")
            field_count = len(fields)
            status = "✓ OK" if field_count == 4 else f"✗ ERROR (found {field_count}/4 fields)"
            print(f"{status} | {fields[0] if fields else 'N/A':8s} | {fields[1] if len(fields) > 1 else 'N/A'}")
            if field_count != 4:
                print(f"     完整内容: {line}")

        return True

    except Exception as e:
        print(f"✗ HanLP 提取失败: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_llm_format_parsing():
    """测试模拟 LLM 输出（包含错误格式）"""
    print("\n" + "="*60)
    print("测试 2: 模拟 LLM 输出格式问题")
    print("="*60 + "\n")

    # 模拟错误的 LLM 输出（5个字段）
    wrong_llm_output = """entity<|#|>沐春风<|#|>person<|#|>主角<|#|>额外字段
entity<|#|>雪松长船<|#|>location<|#|>船只
entity<|#|>三蛇岛<|#|>location<|#|>岛屿<|#|>多余的
<|COMPLETE|>"""

    print("模拟的错误 LLM 输出:\n")
    print(wrong_llm_output)
    print("\n" + "-"*60)
    print("解析结果:")
    print("-"*60 + "\n")

    for line in wrong_llm_output.strip().split('\n'):
        if line == "<|COMPLETE|>":
            continue
        fields = line.split("<|#|>")
        field_count = len(fields)

        if field_count == 4:
            print(f"✓ {fields[1]:10s} - 格式正确")
        else:
            print(f"✗ {fields[1] if len(fields) > 1 else 'N/A':10s} - 格式错误: 发现 {field_count}/4 字段")
            print(f"  WARNING: chunk-xxx: LLM output format error; found {field_count}/4 feilds on ENTITY `{fields[1]}` @ `{fields[2] if len(fields) > 2 else 'N/A'}`")


def main():
    print("\n" + "█"*60)
    print("█" + " "*58 + "█")
    print("█" + "  LightRAG 实体提取来源调试工具".center(56) + "  █")
    print("█" + " "*58 + "█")
    print("█"*60 + "\n")

    # 测试 1: HanLP 提取
    hanlp_ok = test_hanlp_extraction()

    # 测试 2: LLM 格式问题
    test_llm_format_parsing()

    # 总结
    print("\n" + "="*60)
    print("总结:")
    print("="*60)
    print("""
1. HanLP 提取的实体会被转换为标准的 4 字段格式
2. 警告 "found 5/4 feilds" 说明是 LLM 输出了额外字段
3. 可能原因:
   - 你的配置启用了 LLM fallback (use_llm_extraction_fallback=True)
   - HanLP 未找到实体，回退到了 LLM 提取
   - LLM 的 gleaning 步骤产生了格式错误的输出

建议:
- 检查日志中 "Custom extractor found X entities" 的消息
- 如果看到 "falling back to LLM"，说明在使用 LLM
- 如果没有这类消息，说明全部使用 HanLP（格式正确）
    """)


if __name__ == "__main__":
    main()
