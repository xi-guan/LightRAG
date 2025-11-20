#!/usr/bin/env python3
"""
在 LightRAG 中使用三语言实体提取器

演示如何将三语言实体提取器集成到 LightRAG 工作流中，
处理多语言文档并构建知识图谱。
"""

from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor


class MultilingualRAG:
    """支持多语言的 RAG 系统"""

    def __init__(self):
        """初始化"""
        self.extractor = TrilingualEntityExtractor()
        self.knowledge_base = {"entities": [], "relations": []}

    def detect_language(self, text: str) -> str:
        """
        简单的语言检测（实际应用中可使用 langdetect 等库）

        Args:
            text: 输入文本

        Returns:
            语言代码 (zh/en/sv)
        """
        # 简单启发式：检测中文字符
        chinese_chars = sum(1 for c in text if "\u4e00" <= c <= "\u9fff")
        if chinese_chars > len(text) * 0.3:
            return "zh"

        # 检测瑞典语特征字符
        swedish_chars = ["å", "ä", "ö", "Å", "Ä", "Ö"]
        if any(c in text for c in swedish_chars):
            return "sv"

        # 默认为英文
        return "en"

    def extract_entities(self, text: str, language: str = None) -> list:
        """
        提取文本中的实体

        Args:
            text: 输入文本
            language: 语言代码（如果为 None 则自动检测）

        Returns:
            实体列表
        """
        if language is None:
            language = self.detect_language(text)

        print(f"检测到语言: {language}")

        entities = self.extractor.extract(text, language=language)

        # 添加到知识库
        for ent in entities:
            self.knowledge_base["entities"].append(
                {"text": ent["entity"], "type": ent["type"], "language": language}
            )

        return entities

    def build_knowledge_graph(self, documents: list):
        """
        从多语言文档构建知识图谱

        Args:
            documents: 文档列表，每个文档包含 text 和 language (可选)
        """
        print("\n" + "=" * 60)
        print("  构建多语言知识图谱")
        print("=" * 60)

        for i, doc in enumerate(documents, 1):
            text = doc["text"]
            language = doc.get("language")

            print(f"\n处理文档 {i}/{len(documents)}...")
            print(f"内容预览: {text[:100]}...")

            entities = self.extract_entities(text, language)

            print(f"提取到 {len(entities)} 个实体:")
            for ent in entities:
                print(f"  - {ent['entity']} ({ent['type']})")

        print("\n" + "=" * 60)
        print("  知识图谱构建完成")
        print("=" * 60)
        print(f"\n总实体数: {len(self.knowledge_base['entities'])}")

        # 统计每种语言的实体数
        lang_stats = {}
        for ent in self.knowledge_base["entities"]:
            lang = ent["language"]
            lang_stats[lang] = lang_stats.get(lang, 0) + 1

        print("\n语言分布:")
        lang_names = {"zh": "中文", "en": "英文", "sv": "瑞典语"}
        for lang, count in lang_stats.items():
            print(f"  - {lang_names.get(lang, lang)}: {count} 个实体")

    def search(self, query: str, language: str = None) -> list:
        """
        在知识库中搜索

        Args:
            query: 查询文本
            language: 语言代码

        Returns:
            匹配的实体列表
        """
        query_entities = self.extract_entities(query, language)
        query_texts = {ent["entity"] for ent in query_entities}

        # 简单的实体匹配
        results = [
            ent for ent in self.knowledge_base["entities"] if ent["text"] in query_texts
        ]

        return results


def example_simple_extraction():
    """简单提取示例"""
    print("\n" + "=" * 60)
    print("  示例 1: 简单实体提取")
    print("=" * 60)

    rag = MultilingualRAG()

    # 中文文本
    text_zh = "腾讯公司在深圳成立，马化腾是创始人。"
    print(f"\n输入文本: {text_zh}")
    entities = rag.extract_entities(text_zh)
    print(f"提取结果: {[e['entity'] for e in entities]}")

    # 英文文本
    text_en = "Google was founded by Larry Page in California."
    print(f"\n输入文本: {text_en}")
    entities = rag.extract_entities(text_en)
    print(f"提取结果: {[e['entity'] for e in entities]}")


def example_knowledge_graph():
    """知识图谱构建示例"""
    print("\n" + "=" * 60)
    print("  示例 2: 多语言知识图谱构建")
    print("=" * 60)

    rag = MultilingualRAG()

    # 多语言文档集合
    documents = [
        # 中文文档
        {
            "text": "阿里巴巴集团由马云创立于1999年，总部位于杭州。公司业务包括电子商务、云计算、数字媒体等。",
            "language": "zh",
        },
        {
            "text": "华为技术有限公司成立于1987年，创始人任正非，总部在深圳。",
            "language": "zh",
        },
        # 英文文档
        {
            "text": "Amazon was founded by Jeff Bezos in 1994 in Seattle. The company is now one of the largest e-commerce platforms.",
            "language": "en",
        },
        {
            "text": "Microsoft, led by CEO Satya Nadella, is headquartered in Redmond, Washington.",
            "language": "en",
        },
        # 瑞典语文档
        {
            "text": "Spotify grundades av Daniel Ek och Martin Lorentzon i Stockholm 2006. Företaget är en av världens största musiktjänster.",
            "language": "sv",
        },
        {
            "text": "Ericsson grundades 1876 av Lars Magnus Ericsson i Stockholm.",
            "language": "sv",
        },
    ]

    rag.build_knowledge_graph(documents)


def example_auto_language_detection():
    """自动语言检测示例"""
    print("\n" + "=" * 60)
    print("  示例 3: 自动语言检测")
    print("=" * 60)

    rag = MultilingualRAG()

    texts = [
        "比亚迪是中国最大的电动车制造商之一。",
        "Tesla is an American electric vehicle manufacturer.",
        "Volvo är en svensk biltillverkare.",
    ]

    for text in texts:
        print(f"\n文本: {text}")
        entities = rag.extract_entities(text)  # 不指定语言，自动检测
        print(f"实体: {[e['entity'] for e in entities]}")


def example_search():
    """搜索示例"""
    print("\n" + "=" * 60)
    print("  示例 4: 知识库搜索")
    print("=" * 60)

    rag = MultilingualRAG()

    # 先构建知识库
    documents = [
        {
            "text": "苹果公司的CEO是蒂姆·库克，总部在加利福尼亚州库比蒂诺。",
            "language": "zh",
        },
        {
            "text": "Apple Inc. CEO Tim Cook leads the company from Cupertino.",
            "language": "en",
        },
    ]

    print("\n构建知识库...")
    rag.build_knowledge_graph(documents)

    # 搜索
    query = "蒂姆·库克在哪里工作？"
    print(f"\n查询: {query}")
    results = rag.search(query, language="zh")

    print(f"\n找到 {len(results)} 个相关实体:")
    for r in results:
        print(f"  - {r['text']} ({r['type']}) [{r['language']}]")


def performance_tips():
    """性能优化提示"""
    print("\n" + "=" * 60)
    print("  性能优化提示")
    print("=" * 60)

    tips = """
    1. 延迟加载 (Lazy Loading)
       - 模型只在首次使用时加载
       - 同时只加载一个语言模型
       - 内存占用: ~1.5-1.8 GB (而非 4-5 GB)

    2. 批处理 (Batch Processing)
       - spaCy 支持批处理，可提升 2-3 倍速度
       - 示例: extractor.spacy_en.pipe(texts)

    3. GPU 加速
       - spaCy 的 Transformer 模型支持 GPU
       - 需要安装: pip install spacy[cuda]

    4. 模型选择
       - 英文: en_core_web_trf (最高质量) vs en_core_web_sm (更快)
       - 瑞典语: sv_core_news_lg (推荐) vs sv_core_news_sm (更快)
       - 中文: HanLP 只有一个模型选项

    5. 缓存结果
       - 对于重复文本，缓存提取结果
       - 可使用 functools.lru_cache 或 Redis
    """
    print(tips)


def integration_guide():
    """集成指南"""
    print("\n" + "=" * 60)
    print("  集成到现有 LightRAG 工作流")
    print("=" * 60)

    guide = """
    方法 1: 替换默认实体提取器
    ──────────────────────────────
    from lightrag import LightRAG
    from lightrag.kg.trilingual_entity_extractor import TrilingualEntityExtractor

    # 创建 LightRAG 实例
    rag = LightRAG(
        working_dir="./rag_storage",
        llm_model_func=your_llm_model,
    )

    # 替换实体提取器
    rag.entity_extractor = TrilingualEntityExtractor()

    # 使用时指定语言
    rag.insert("your text", language="zh")


    方法 2: 预处理文档
    ──────────────────────────────
    extractor = TrilingualEntityExtractor()

    # 先提取实体
    entities = extractor.extract(text, language="zh")

    # 将实体注入到 LightRAG
    for ent in entities:
        rag.add_entity(ent['entity'], ent['type'])


    方法 3: 混合模式
    ──────────────────────────────
    # 对于高质量要求的文档，使用三语言提取器
    if is_important(doc):
        entities = trilingual_extractor.extract(doc.text, doc.language)
    # 对于一般文档，使用 LLM 提取（更灵活但成本更高）
    else:
        entities = llm_extractor.extract(doc.text)
    """
    print(guide)


def main():
    """主函数"""
    print("=" * 60)
    print("  LightRAG 三语言实体提取器 - 实际应用示例")
    print("=" * 60)

    try:
        # 示例 1: 简单提取
        example_simple_extraction()

        # 示例 2: 知识图谱构建
        example_knowledge_graph()

        # 示例 3: 自动语言检测
        example_auto_language_detection()

        # 示例 4: 搜索
        example_search()

        # 性能优化提示
        performance_tips()

        # 集成指南
        integration_guide()

        print("\n" + "=" * 60)
        print("  ✅ 所有示例运行成功！")
        print("=" * 60)
        print()
        print("下一步:")
        print("  1. 运行基础示例: python examples/trilingual_extractor_demo.py")
        print("  2. 运行完整测试: python scripts/test_trilingual_extractor.py")
        print("  3. 查看文档: docs/TrilingualNER-Usage-zh.md")
        print("  4. 集成到你的项目中")
        print()

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        print("\n请确保:")
        print("  1. 已安装依赖: uv sync --extra trilingual")
        print("  2. 已下载模型: ./scripts/install_trilingual_models.sh")
        import traceback

        traceback.print_exc()


if __name__ == "__main__":
    main()
