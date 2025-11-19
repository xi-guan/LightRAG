#!/usr/bin/env python3
"""
LightRAG 索引速度对比测试

对比使用 LLM 提取 vs 使用三语言实体提取器的实际索引速度
"""

import requests
import time
import json
from datetime import datetime


def test_indexing_speed(
    base_url="http://localhost:9621", num_documents=50, use_trilingual=True
):
    """
    测试索引速度

    Args:
        base_url: 服务器地址
        num_documents: 测试文档数量
        use_trilingual: 是否使用三语言提取器
    """
    print("\n" + "=" * 70)
    mode = "三语言实体提取器" if use_trilingual else "LLM 提取"
    print(f"  测试: {mode}")
    print("=" * 70)

    # 测试文档（中文）
    test_documents = [
        "腾讯公司由马化腾创立于1998年11月，总部位于广东省深圳市。公司主营业务包括社交网络、即时通讯、网络游戏、数字内容、金融科技等。",
        "阿里巴巴集团由马云创立于1999年，总部位于浙江省杭州市。集团业务包括电子商务、云计算、数字媒体和娱乐、物流等领域。",
        "华为技术有限公司成立于1987年，创始人任正非，总部在深圳。华为是全球领先的信息与通信技术解决方案供应商。",
        "百度公司由李彦宏创立于2000年1月，总部位于北京市海淀区。百度是中国最大的搜索引擎和AI技术公司。",
        "字节跳动成立于2012年，创始人张一鸣，总部位于北京。公司旗下产品包括抖音、今日头条、TikTok等。",
        "京东集团由刘强东创立于1998年，总部位于北京市。京东是中国最大的自营式电商企业。",
        "美团由王兴创立于2010年3月，总部位于北京市。美团是中国领先的生活服务电子商务平台。",
        "小米科技由雷军创立于2010年4月，总部位于北京市。小米是全球第三大智能手机制造商。",
        "网易公司由丁磊创立于1997年，总部位于广州市。网易是中国领先的互联网技术公司。",
        "拼多多由黄峥创立于2015年，总部位于上海市。拼多多是中国新电商平台。",
    ]

    # 重复文档以达到目标数量
    documents = (test_documents * (num_documents // len(test_documents) + 1))[
        :num_documents
    ]

    print(f"\n测试配置:")
    print(f"  - 文档数量: {len(documents)}")
    print(f"  - 提取模式: {mode}")
    print(f"  - 服务器: {base_url}")

    # 开始测试
    print(f"\n开始索引...")
    start_time = time.time()

    success_count = 0
    failed_count = 0
    times = []

    for i, text in enumerate(documents, 1):
        doc_start = time.time()

        try:
            response = requests.post(
                f"{base_url}/insert",
                json={
                    "text": text,
                    "language": "zh",
                    "use_trilingual": use_trilingual,
                },
                timeout=60,
            )

            doc_time = time.time() - doc_start
            times.append(doc_time)

            if response.status_code == 200:
                success_count += 1
                print(
                    f"  [{i}/{len(documents)}] ✅ 完成 ({doc_time:.2f}s) | 平均: {sum(times)/len(times):.2f}s"
                )
            else:
                failed_count += 1
                print(f"  [{i}/{len(documents)}] ❌ 失败: {response.status_code}")

        except Exception as e:
            failed_count += 1
            print(f"  [{i}/{len(documents)}] ❌ 错误: {e}")

    total_time = time.time() - start_time

    # 统计结果
    print("\n" + "=" * 70)
    print("  测试结果")
    print("=" * 70)
    print(f"\n总文档数: {len(documents)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"\n总耗时: {total_time:.2f} 秒")

    if times:
        avg_time = sum(times) / len(times)
        min_time = min(times)
        max_time = max(times)

        print(f"\n性能指标:")
        print(f"  - 平均时间/文档: {avg_time:.2f} 秒")
        print(f"  - 最快: {min_time:.2f} 秒")
        print(f"  - 最慢: {max_time:.2f} 秒")
        print(f"  - 吞吐量: {len(documents)/total_time:.2f} 文档/秒")
        print(f"  - 预计 1417 chunks: {1417 * avg_time / 60:.1f} 分钟")

    return {
        "mode": mode,
        "total_docs": len(documents),
        "success": success_count,
        "failed": failed_count,
        "total_time": total_time,
        "avg_time_per_doc": sum(times) / len(times) if times else 0,
        "throughput": len(documents) / total_time if total_time > 0 else 0,
    }


def main():
    """主函数"""
    print("=" * 70)
    print("  LightRAG 索引速度对比测试")
    print("=" * 70)
    print()
    print("此测试将对比两种提取模式的实际索引速度:")
    print("  1. LLM 提取 (原始方式)")
    print("  2. 三语言实体提取器 (新方式)")
    print()

    base_url = "http://localhost:9621"

    # 检查服务器
    print(f"检查服务器: {base_url}")
    try:
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code == 200:
            print("✅ 服务器运行正常")
        else:
            print("❌ 服务器响应异常")
            return
    except Exception as e:
        print(f"❌ 无法连接到服务器: {e}")
        print()
        print("请先启动 LightRAG server:")
        print("  ./scripts/start_server_with_trilingual.sh")
        return

    # 询问测试数量
    print()
    try:
        num_docs = int(input("输入测试文档数量 (建议 50-100): ") or "50")
    except (ValueError, KeyboardInterrupt, EOFError):
        num_docs = 50

    print()
    print(f"将使用 {num_docs} 个文档进行测试...")
    print()

    # 测试 1: LLM 提取
    print("\n" + "🔵" * 35)
    print("  第一轮: LLM 提取 (原始方式)")
    print("🔵" * 35)
    input("\n按 Enter 开始测试 1...")

    result_llm = test_indexing_speed(
        base_url=base_url, num_documents=num_docs, use_trilingual=False
    )

    # 等待用户确认
    print()
    print("测试 1 完成！")
    input("\n按 Enter 继续测试 2...")

    # 测试 2: 三语言提取器
    print("\n" + "🟢" * 35)
    print("  第二轮: 三语言实体提取器")
    print("🟢" * 35)
    input("\n按 Enter 开始测试 2...")

    result_trilingual = test_indexing_speed(
        base_url=base_url, num_documents=num_docs, use_trilingual=True
    )

    # 对比结果
    print("\n\n" + "=" * 70)
    print("  性能对比总结")
    print("=" * 70)

    print(f"\n📊 测试规模: {num_docs} 个文档")
    print()

    print("┌─────────────────────────┬──────────────┬──────────────┬──────────┐")
    print("│ 指标                    │ LLM 提取     │ 三语言提取器 │ 提升     │")
    print("├─────────────────────────┼──────────────┼──────────────┼──────────┤")

    # 总耗时
    speedup_total = result_llm["total_time"] / result_trilingual["total_time"]
    print(
        f"│ 总耗时                  │ {result_llm['total_time']:>9.1f}s │ {result_trilingual['total_time']:>9.1f}s │ {speedup_total:>5.1f}x │"
    )

    # 平均时间
    speedup_avg = result_llm["avg_time_per_doc"] / result_trilingual["avg_time_per_doc"]
    print(
        f"│ 平均时间/文档           │ {result_llm['avg_time_per_doc']:>9.2f}s │ {result_trilingual['avg_time_per_doc']:>9.2f}s │ {speedup_avg:>5.1f}x │"
    )

    # 吞吐量
    print(
        f"│ 吞吐量 (文档/秒)        │ {result_llm['throughput']:>9.2f}  │ {result_trilingual['throughput']:>9.2f}  │ {speedup_avg:>5.1f}x │"
    )

    print("└─────────────────────────┴──────────────┴──────────────┴──────────┘")

    # 预测 1417 chunks
    print()
    print("📈 预测你的实际场景 (1417 chunks):")
    time_llm = result_llm["avg_time_per_doc"] * 1417 / 60
    time_trilingual = result_trilingual["avg_time_per_doc"] * 1417 / 60
    saved_time = time_llm - time_trilingual

    print(f"  - LLM 提取: {time_llm:.1f} 分钟 ({time_llm/60:.1f} 小时)")
    print(
        f"  - 三语言提取: {time_trilingual:.1f} 分钟 ({time_trilingual/60:.1f} 小时)"
    )
    print(f"  - 节省时间: {saved_time:.1f} 分钟 ({saved_time/60:.1f} 小时)")
    print(f"  - 速度提升: {speedup_avg:.1f}x")

    # 结论
    print()
    print("=" * 70)
    if speedup_avg > 1.5:
        print("  ✅ 结论: 三语言实体提取器显著提升了索引速度！")
    elif speedup_avg > 1.1:
        print("  ✅ 结论: 三语言实体提取器有一定速度提升。")
    else:
        print("  ⚠️  结论: 速度提升不明显，可能需要检查配置。")
    print("=" * 70)

    # 保存结果
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_file = f"benchmark_result_{timestamp}.json"

    with open(result_file, "w", encoding="utf-8") as f:
        json.dump(
            {
                "timestamp": timestamp,
                "num_documents": num_docs,
                "llm_extraction": result_llm,
                "trilingual_extraction": result_trilingual,
                "speedup": speedup_avg,
            },
            f,
            indent=2,
            ensure_ascii=False,
        )

    print()
    print(f"📝 测试结果已保存到: {result_file}")
    print()


if __name__ == "__main__":
    main()
