"""
三语言实体提取器（中文/英文/瑞典语）

使用最佳工具组合：
- 中文: HanLP (F1 95%)
- 英文: spaCy (F1 90%)
- 瑞典语: spaCy (F1 80-85%)

特点：
- 延迟加载（按需加载模型，节省内存）
- 高质量（每种语言使用最佳工具）
- 简单易用
"""

from typing import List, Dict, Literal
import logging

logger = logging.getLogger(__name__)


class TrilingualEntityExtractor:
    """三语言实体提取器（中/英/瑞典）"""

    def __init__(
        self,
        chinese_model: str = "CLOSE_TOK_POS_NER_SRL_DEP_SDP_CON_ELECTRA_BASE_ZH",
        english_model: str = "en_core_web_trf",
        swedish_model: str = "sv_core_news_lg",
    ):
        """初始化（延迟加载模型）

        Args:
            chinese_model: HanLP 中文模型名称
            english_model: spaCy 英文模型名称
            swedish_model: spaCy 瑞典语模型名称
        """
        self._spacy_en = None
        self._spacy_sv = None
        self._hanlp = None
        self.chinese_model = chinese_model
        self.english_model = english_model
        self.swedish_model = swedish_model

    @property
    def spacy_en(self):
        """延迟加载英文模型"""
        if self._spacy_en is None:
            logger.info(f"Loading English spaCy model ({self.english_model})...")
            try:
                import spacy

                self._spacy_en = spacy.load(self.english_model)
                logger.info("✓ English model loaded successfully")
            except OSError:
                logger.error(
                    f"English model not found. Please run: "
                    f"python -m spacy download {self.english_model}"
                )
                raise
        return self._spacy_en

    @property
    def spacy_sv(self):
        """延迟加载瑞典语模型"""
        if self._spacy_sv is None:
            logger.info(f"Loading Swedish spaCy model ({self.swedish_model})...")
            try:
                import spacy

                self._spacy_sv = spacy.load(self.swedish_model)
                logger.info("✓ Swedish model loaded successfully")
            except OSError:
                logger.error(
                    f"Swedish model not found. Please run: "
                    f"python -m spacy download {self.swedish_model}"
                )
                raise
        return self._spacy_sv

    @property
    def hanlp(self):
        """延迟加载中文模型"""
        if self._hanlp is None:
            logger.info(f"Loading Chinese HanLP model ({self.chinese_model})...")
            try:
                import hanlp

                # Try to get model from hanlp.pretrained.mtl first
                model_path = None
                if hasattr(hanlp.pretrained.mtl, self.chinese_model):
                    model_path = getattr(hanlp.pretrained.mtl, self.chinese_model)
                else:
                    # Fallback: use chinese_model as direct path
                    model_path = self.chinese_model

                self._hanlp = hanlp.load(model_path)
                logger.info("✓ Chinese model loaded successfully")
            except Exception as e:
                logger.error(f"Failed to load HanLP model: {e}")
                raise
        return self._hanlp

    def extract(
        self, text: str, language: Literal["zh", "en", "sv"]
    ) -> List[Dict[str, any]]:
        """提取实体

        Args:
            text: 文本内容
            language: 'zh' (中文), 'en' (英文), 'sv' (瑞典语)

        Returns:
            [{'entity': '...', 'type': '...', 'score': 0.9, 'start': 0, 'end': 5}, ...]

        Raises:
            ValueError: 如果语言不支持
        """
        logger.debug(
            f"Extracting entities for language '{language}' (text length: {len(text)})"
        )

        if language == "zh":
            return self._extract_chinese(text)
        elif language == "en":
            return self._extract_english(text)
        elif language == "sv":
            return self._extract_swedish(text)
        else:
            raise ValueError(
                f"Unsupported language: {language}. " f"Supported: 'zh', 'en', 'sv'"
            )

    def _extract_chinese(self, text: str) -> List[Dict]:
        """提取中文实体（使用 HanLP）

        HanLP 输出格式：
        {
            'tok': [['苹果', '公司'], ...],
            'ner': [['B-ORG', 'I-ORG'], ...]
        }
        """
        # Request both tok (tokenization) and ner (named entity recognition)
        logger.debug(f"Calling HanLP with model: {self.chinese_model}")
        try:
            result = self.hanlp(text, tasks=["tok", "ner"])
            logger.debug(
                f"HanLP returned result type: {type(result).__name__}, "
                f"keys: {list(result.keys()) if isinstance(result, dict) else 'N/A'}"
            )
        except Exception as e:
            logger.error(
                f"HanLP processing failed for text (length={len(text)}): {type(e).__name__}: {e}"
            )
            raise RuntimeError(
                f"HanLP processing failed for text (length={len(text)}): {e}"
            ) from e

        # Validate that result contains required keys
        if not isinstance(result, dict):
            raise ValueError(
                f"Expected dict from HanLP, got {type(result).__name__}. "
                f"This may indicate an incompatible HanLP model or version."
            )

        if "tok" not in result:
            raise KeyError(
                f"HanLP result missing 'tok' key. Available keys: {list(result.keys())}. "
                f"Please ensure your HanLP model ({self.chinese_model}) supports the 'tok' task."
            )

        if "ner" not in result:
            raise KeyError(
                f"HanLP result missing 'ner' key. Available keys: {list(result.keys())}. "
                f"Please ensure your HanLP model ({self.chinese_model}) supports the 'ner' task."
            )

        entities = []
        current_entity = []
        current_type = None
        current_start = 0
        char_position = 0

        # 遍历 token 和 NER 标签
        for tokens, labels in zip(result["tok"], result["ner"]):
            for token, label in zip(tokens, labels):
                if label.startswith("B-"):  # Begin of entity
                    # 保存之前的实体
                    if current_entity:
                        entities.append(
                            {
                                "entity": "".join(current_entity),
                                "type": current_type,
                                "score": 1.0,
                                "start": current_start,
                                "end": char_position,
                            }
                        )

                    # 开始新实体
                    current_entity = [token]
                    current_type = label[2:]  # 去掉 'B-' 前缀
                    current_start = char_position

                elif label.startswith("I-") and current_entity:  # Inside entity
                    current_entity.append(token)

                else:  # O (Outside) or 结束当前实体
                    if current_entity:
                        entities.append(
                            {
                                "entity": "".join(current_entity),
                                "type": current_type,
                                "score": 1.0,
                                "start": current_start,
                                "end": char_position,
                            }
                        )
                        current_entity = []
                        current_type = None

                char_position += len(token)

        # 处理最后一个实体
        if current_entity:
            entities.append(
                {
                    "entity": "".join(current_entity),
                    "type": current_type,
                    "score": 1.0,
                    "start": current_start,
                    "end": char_position,
                }
            )

        return entities

    def _extract_english(self, text: str) -> List[Dict]:
        """提取英文实体（使用 spaCy）"""
        doc = self.spacy_en(text)
        return [
            {
                "entity": ent.text,
                "type": ent.label_,
                "score": 1.0,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]

    def _extract_swedish(self, text: str) -> List[Dict]:
        """提取瑞典语实体（使用 spaCy）"""
        doc = self.spacy_sv(text)
        return [
            {
                "entity": ent.text,
                "type": ent.label_,
                "score": 1.0,
                "start": ent.start_char,
                "end": ent.end_char,
            }
            for ent in doc.ents
        ]

    def unload_all(self):
        """卸载所有模型（释放内存）"""
        logger.info("Unloading all models to free memory...")
        self._spacy_en = None
        self._spacy_sv = None
        self._hanlp = None
        logger.info("✓ All models unloaded")

    def get_loaded_models(self) -> List[str]:
        """获取当前已加载的模型列表"""
        loaded = []
        if self._spacy_en is not None:
            loaded.append("English (spaCy)")
        if self._spacy_sv is not None:
            loaded.append("Swedish (spaCy)")
        if self._hanlp is not None:
            loaded.append("Chinese (HanLP)")
        return loaded


# 便捷函数
def create_extractor() -> TrilingualEntityExtractor:
    """创建三语言实体提取器实例

    Returns:
        TrilingualEntityExtractor 实例

    Example:
        >>> extractor = create_extractor()
        >>> entities = extractor.extract("Apple Inc. was founded in 1976.", language='en')
        >>> print(entities)
        [{'entity': 'Apple Inc.', 'type': 'ORG', 'score': 1.0, ...}, ...]
    """
    return TrilingualEntityExtractor()
