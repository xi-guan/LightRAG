#!/usr/bin/env python3
"""
LightRAG 实时索引测试 - 上传文档并查看提取速度

使用三语言实体提取器实时索引文档，显示提取的实体和耗时
"""

import requests
import time
import sys
from pathlib import Path


def upload_document(server_url, text, language="zh", use_trilingual=True):
    """
    上传单个文档到 LightRAG

    Args:
        server_url: 服务器地址
        text: 文档内容
        language: 语言代码
        use_trilingual: 是否使用三语言提取器

    Returns:
        响应结果和耗时
    """
    print("\n" + "=" * 70)
    print(f"  上传文档 ({'三语言提取器' if use_trilingual else 'LLM 提取'})")
    print("=" * 70)

    print(f"\n📄 文档内容:")
    print(f"  {text[:200]}{'...' if len(text) > 200 else ''}")
    print(f"\n📊 配置:")
    print(f"  - 语言: {language}")
    print(f"  - 提取器: {'三语言' if use_trilingual else 'LLM'}")

    # 记录开始时间
    start_time = time.time()

    try:
        response = requests.post(
            f"{server_url}/insert",
            json={"text": text, "language": language, "use_trilingual": use_trilingual},
            timeout=120,
        )

        elapsed_time = time.time() - start_time

        if response.status_code == 200:
            result = response.json()

            print(f"\n✅ 上传成功！")
            print(f"\n⏱️  耗时: {elapsed_time:.2f} 秒")

            # 显示提取的实体
            if "entities" in result:
                entities = result["entities"]
                print(f"\n🎯 提取的实体 ({len(entities)} 个):")
                for i, ent in enumerate(entities[:20], 1):  # 最多显示 20 个
                    print(f"  {i}. {ent.get('entity', 'N/A')}: {ent.get('type', 'N/A')}")
                if len(entities) > 20:
                    print(f"  ... 还有 {len(entities) - 20} 个实体")

            # 显示提取的关系
            if "relations" in result:
                relations = result["relations"]
                print(f"\n🔗 提取的关系 ({len(relations)} 个):")
                for i, rel in enumerate(relations[:10], 1):  # 最多显示 10 个
                    print(f"  {i}. {rel.get('source', 'N/A')} → {rel.get('relation', 'N/A')} → {rel.get('target', 'N/A')}")
                if len(relations) > 10:
                    print(f"  ... 还有 {len(relations) - 10} 个关系")

            return {"success": True, "time": elapsed_time, "result": result}

        else:
            print(f"\n❌ 上传失败: {response.status_code}")
            print(f"  错误信息: {response.text}")
            return {"success": False, "time": elapsed_time, "error": response.text}

    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"\n❌ 错误: {e}")
        return {"success": False, "time": elapsed_time, "error": str(e)}


def upload_file(server_url, file_path, language="zh", use_trilingual=True):
    """
    从文件上传文档

    Args:
        server_url: 服务器地址
        file_path: 文件路径
        language: 语言代码
        use_trilingual: 是否使用三语言提取器
    """
    file_path = Path(file_path)

    if not file_path.exists():
        print(f"❌ 文件不存在: {file_path}")
        return

    print(f"\n📂 读取文件: {file_path}")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    print(f"  文件大小: {len(text)} 字符")

    return upload_document(server_url, text, language, use_trilingual)


def batch_upload(server_url, texts, language="zh", use_trilingual=True):
    """
    批量上传文档

    Args:
        server_url: 服务器地址
        texts: 文档列表
        language: 语言代码
        use_trilingual: 是否使用三语言提取器
    """
    print("\n" + "=" * 70)
    print(f"  批量上传 {len(texts)} 个文档")
    print("=" * 70)

    results = []
    total_start = time.time()

    for i, text in enumerate(texts, 1):
        print(f"\n进度: [{i}/{len(texts)}]")
        result = upload_document(server_url, text, language, use_trilingual)
        results.append(result)

        # 简短的摘要
        if result["success"]:
            print(f"  ✅ 成功 ({result['time']:.2f}s)")
        else:
            print(f"  ❌ 失败")

    total_time = time.time() - total_start

    # 统计
    print("\n" + "=" * 70)
    print("  批量上传总结")
    print("=" * 70)

    success_count = sum(1 for r in results if r["success"])
    failed_count = len(results) - success_count

    print(f"\n总文档数: {len(texts)}")
    print(f"成功: {success_count}")
    print(f"失败: {failed_count}")
    print(f"\n总耗时: {total_time:.2f} 秒")

    if success_count > 0:
        success_times = [r["time"] for r in results if r["success"]]
        avg_time = sum(success_times) / len(success_times)
        print(f"平均时间/文档: {avg_time:.2f} 秒")
        print(f"吞吐量: {success_count / total_time:.2f} 文档/秒")


def main():
    """主函数"""
    print("=" * 70)
    print("  LightRAG 实时索引测试")
    print("=" * 70)

    server_url = "http://localhost:9621"

    # 检查服务器
    print(f"\n检查服务器: {server_url}")
    try:
        response = requests.get(f"{server_url}/health", timeout=5)
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

    # 示例文档
    sample_documents = [
        "腾讯公司由马化腾创立于1998年11月，总部位于广东省深圳市。公司主营业务包括社交网络、即时通讯、网络游戏、数字内容、金融科技等。腾讯是中国最大的互联网公司之一。",
        "阿里巴巴集团由马云创立于1999年，总部位于浙江省杭州市。集团业务包括电子商务、云计算、数字媒体和娱乐、物流等领域。阿里巴巴是全球最大的零售商务平台。",
        "华为技术有限公司成立于1987年，创始人任正非，总部在深圳。华为是全球领先的信息与通信技术解决方案供应商，业务遍及170多个国家和地区。",
    ]

    # 选择模式
    print()
    print("选择测试模式:")
    print("  1. 上传单个文档")
    print("  2. 批量上传示例文档 (3个)")
    print("  3. 从文件上传")

    try:
        choice = input("\n选择 (1-3): ").strip() or "1"
    except:
        choice = "1"

    # 选择提取器
    print()
    print("选择提取器:")
    print("  1. 三语言实体提取器 (快)")
    print("  2. LLM 提取 (慢)")

    try:
        extractor = input("\n选择 (1-2): ").strip() or "1"
        use_trilingual = extractor == "1"
    except:
        use_trilingual = True

    if choice == "1":
        # 单个文档
        print()
        print("输入文档内容 (按 Ctrl+D 或 Ctrl+Z 结束):")
        try:
            text = sys.stdin.read().strip()
            if text:
                upload_document(server_url, text, "zh", use_trilingual)
            else:
                print("\n使用默认示例文档...")
                upload_document(server_url, sample_documents[0], "zh", use_trilingual)
        except:
            print("\n使用默认示例文档...")
            upload_document(server_url, sample_documents[0], "zh", use_trilingual)

    elif choice == "2":
        # 批量上传
        batch_upload(server_url, sample_documents, "zh", use_trilingual)

    elif choice == "3":
        # 从文件上传
        print()
        file_path = input("输入文件路径: ").strip()
        if file_path:
            upload_file(server_url, file_path, "zh", use_trilingual)
        else:
            print("未提供文件路径")

    print()
    print("=" * 70)
    print("  测试完成")
    print("=" * 70)


if __name__ == "__main__":
    main()
