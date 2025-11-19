#!/usr/bin/env python3
"""
LightRAG Server 三语言实体提取器测试脚本

测试 LightRAG API 服务器与三语言实体提取器的集成。
"""

import requests
import json
import time
import sys


class ServerTester:
    """LightRAG 服务器测试器"""

    def __init__(self, base_url="http://localhost:9621"):
        """
        初始化测试器

        Args:
            base_url: 服务器地址
        """
        self.base_url = base_url
        self.session = requests.Session()

    def test_connection(self):
        """测试服务器连接"""
        print("\n" + "=" * 60)
        print("  测试 1: 服务器连接")
        print("=" * 60)

        try:
            response = self.session.get(f"{self.base_url}/health")
            if response.status_code == 200:
                print("✅ 服务器连接成功")
                print(f"   状态: {response.json()}")
                return True
            else:
                print(f"❌ 服务器响应异常: {response.status_code}")
                return False
        except requests.exceptions.ConnectionError:
            print("❌ 无法连接到服务器")
            print(f"   请确保服务器运行在: {self.base_url}")
            print("   启动命令: uv run lightrag-server")
            return False

    def test_chinese_extraction(self):
        """测试中文实体提取"""
        print("\n" + "=" * 60)
        print("  测试 2: 中文实体提取")
        print("=" * 60)

        text = "腾讯公司由马化腾创立于1998年，总部位于深圳。公司业务包括社交网络、游戏、云计算等领域。"

        data = {"text": text, "language": "zh", "mode": "entity_extraction"}

        print(f"\n输入文本:")
        print(f"  {text}")

        try:
            response = self.session.post(
                f"{self.base_url}/extract", json=data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                entities = result.get("entities", [])

                print(f"\n✅ 提取成功 ({len(entities)} 个实体):")
                for ent in entities:
                    print(f"  - {ent['entity']}: {ent['type']}")

                return True
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   {response.text}")
                return False

        except Exception as e:
            print(f"❌ 错误: {e}")
            return False

    def test_english_extraction(self):
        """测试英文实体提取"""
        print("\n" + "=" * 60)
        print("  测试 3: 英文实体提取")
        print("=" * 60)

        text = "Microsoft was founded by Bill Gates and Paul Allen in 1975 in Seattle. The company is now led by CEO Satya Nadella."

        data = {"text": text, "language": "en", "mode": "entity_extraction"}

        print(f"\n输入文本:")
        print(f"  {text}")

        try:
            response = self.session.post(
                f"{self.base_url}/extract", json=data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                entities = result.get("entities", [])

                print(f"\n✅ 提取成功 ({len(entities)} 个实体):")
                for ent in entities:
                    print(f"  - {ent['entity']}: {ent['type']}")

                return True
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   {response.text}")
                return False

        except Exception as e:
            print(f"❌ 错误: {e}")
            return False

    def test_swedish_extraction(self):
        """测试瑞典语实体提取"""
        print("\n" + "=" * 60)
        print("  测试 4: 瑞典语实体提取")
        print("=" * 60)

        text = "Spotify grundades av Daniel Ek och Martin Lorentzon i Stockholm 2006. Företaget är nu en av världens största musiktjänster."

        data = {"text": text, "language": "sv", "mode": "entity_extraction"}

        print(f"\n输入文本:")
        print(f"  {text}")

        try:
            response = self.session.post(
                f"{self.base_url}/extract", json=data, timeout=30
            )

            if response.status_code == 200:
                result = response.json()
                entities = result.get("entities", [])

                print(f"\n✅ 提取成功 ({len(entities)} 个实体):")
                for ent in entities:
                    print(f"  - {ent['entity']}: {ent['type']}")

                return True
            else:
                print(f"❌ 请求失败: {response.status_code}")
                print(f"   {response.text}")
                return False

        except Exception as e:
            print(f"❌ 错误: {e}")
            return False

    def test_batch_extraction(self):
        """测试批量提取"""
        print("\n" + "=" * 60)
        print("  测试 5: 批量多语言提取")
        print("=" * 60)

        documents = [
            {"text": "阿里巴巴集团由马云创立于1999年", "language": "zh"},
            {"text": "Amazon was founded by Jeff Bezos in 1994", "language": "en"},
            {"text": "Volvo grundades av Assar Gabrielsson 1927", "language": "sv"},
        ]

        print(f"\n批量处理 {len(documents)} 个文档...")

        results = []
        for i, doc in enumerate(documents, 1):
            print(f"\n文档 {i}/{len(documents)} ({doc['language']}):")
            print(f"  {doc['text']}")

            data = {
                "text": doc["text"],
                "language": doc["language"],
                "mode": "entity_extraction",
            }

            try:
                response = self.session.post(
                    f"{self.base_url}/extract", json=data, timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    entities = result.get("entities", [])
                    print(f"  ✅ {len(entities)} 个实体: {[e['entity'] for e in entities]}")
                    results.append(True)
                else:
                    print(f"  ❌ 失败: {response.status_code}")
                    results.append(False)

            except Exception as e:
                print(f"  ❌ 错误: {e}")
                results.append(False)

        success_rate = sum(results) / len(results) * 100
        print(f"\n批量处理成功率: {success_rate:.0f}% ({sum(results)}/{len(results)})")

        return all(results)

    def test_insert_and_query(self):
        """测试插入和查询"""
        print("\n" + "=" * 60)
        print("  测试 6: 文档插入和查询")
        print("=" * 60)

        # 插入中文文档
        insert_data = {
            "text": "比亚迪是中国最大的电动车制造商之一，总部位于深圳。",
            "language": "zh",
            "mode": "insert",
        }

        print("\n插入文档:")
        print(f"  {insert_data['text']}")

        try:
            response = self.session.post(
                f"{self.base_url}/documents", json=insert_data, timeout=30
            )

            if response.status_code == 200:
                print("  ✅ 文档插入成功")

                # 等待索引完成
                time.sleep(2)

                # 查询
                query_data = {"query": "比亚迪在哪里？", "language": "zh", "mode": "query"}

                print("\n执行查询:")
                print(f"  {query_data['query']}")

                response = self.session.post(
                    f"{self.base_url}/query", json=query_data, timeout=30
                )

                if response.status_code == 200:
                    result = response.json()
                    print("  ✅ 查询成功")
                    print(f"  答案: {result.get('answer', 'N/A')}")
                    return True
                else:
                    print(f"  ❌ 查询失败: {response.status_code}")
                    return False

            else:
                print(f"  ❌ 插入失败: {response.status_code}")
                return False

        except Exception as e:
            print(f"  ❌ 错误: {e}")
            return False

    def test_performance(self):
        """测试性能"""
        print("\n" + "=" * 60)
        print("  测试 7: 性能基准")
        print("=" * 60)

        test_text = "苹果公司由史蒂夫·乔布斯创立。" * 10  # 重复文本

        data = {"text": test_text, "language": "zh", "mode": "entity_extraction"}

        num_requests = 10
        times = []

        print(f"\n执行 {num_requests} 次请求...")

        for i in range(num_requests):
            start_time = time.time()

            try:
                response = self.session.post(
                    f"{self.base_url}/extract", json=data, timeout=30
                )

                elapsed = time.time() - start_time
                times.append(elapsed)

                if response.status_code == 200:
                    print(f"  请求 {i+1}: ✅ {elapsed:.3f}s")
                else:
                    print(f"  请求 {i+1}: ❌ {response.status_code}")

            except Exception as e:
                print(f"  请求 {i+1}: ❌ {e}")

        if times:
            avg_time = sum(times) / len(times)
            min_time = min(times)
            max_time = max(times)

            print(f"\n性能统计:")
            print(f"  平均响应时间: {avg_time:.3f}s")
            print(f"  最快响应: {min_time:.3f}s")
            print(f"  最慢响应: {max_time:.3f}s")
            print(f"  吞吐量: {1/avg_time:.1f} 请求/秒")

            return True

        return False


def main():
    """主函数"""
    print("=" * 60)
    print("  LightRAG Server 三语言实体提取器测试")
    print("=" * 60)

    # 解析命令行参数
    server_url = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:9621"

    print(f"\n服务器地址: {server_url}")
    print("\n提示:")
    print("  - 确保 LightRAG server 已启动")
    print("  - 启动命令: uv run lightrag-server")
    print("  - 或使用自定义地址: python test_server_trilingual.py http://your-server:port")

    # 创建测试器
    tester = ServerTester(server_url)

    # 运行测试
    results = []

    # 1. 连接测试
    if not tester.test_connection():
        print("\n❌ 服务器连接失败，终止测试")
        sys.exit(1)

    results.append(("服务器连接", True))

    # 2. 中文提取
    results.append(("中文实体提取", tester.test_chinese_extraction()))

    # 3. 英文提取
    results.append(("英文实体提取", tester.test_english_extraction()))

    # 4. 瑞典语提取
    results.append(("瑞典语实体提取", tester.test_swedish_extraction()))

    # 5. 批量提取
    results.append(("批量提取", tester.test_batch_extraction()))

    # 6. 插入和查询
    results.append(("文档插入和查询", tester.test_insert_and_query()))

    # 7. 性能测试
    results.append(("性能基准", tester.test_performance()))

    # 总结
    print("\n" + "=" * 60)
    print("  测试总结")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"\n测试结果: {passed}/{total} 通过")

    for name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"  {status}: {name}")

    if passed == total:
        print("\n🎉 所有测试通过！")
        sys.exit(0)
    else:
        print(f"\n⚠️  {total - passed} 个测试失败")
        sys.exit(1)


if __name__ == "__main__":
    main()
