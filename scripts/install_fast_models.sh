#!/bin/bash
# 快速实体提取器安装脚本
# 自动安装 spaCy + HanLP 及相关模型（8-15倍速度提升）

set -e  # 遇到错误立即退出

echo "=================================================="
echo "  快速实体提取器安装"
echo "  支持: 中文 (HanLP) + 英文 (spaCy) + 瑞典语 (spaCy)"
echo "=================================================="
echo ""

# 检查 Python 版本
echo "→ 检查 Python 版本..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python 版本: $python_version"

# 安装 Python 依赖
echo ""
echo "→ 安装 Python 依赖包..."
echo "  - spaCy (英文 + 瑞典语)"
echo "  - HanLP (中文)"
echo ""

# 检查是否安装了 uv
if command -v uv &> /dev/null; then
    echo "  使用 uv 安装 (超快速!)..."
    uv pip install -e ".[fast]"
    uv pip install pip  # 确保虚拟环境有 pip (spacy download 需要)
else
    echo "  使用 pip 安装..."
    echo "  ! 提示: 安装 uv 可获得 10-100 倍速度提升"
    echo "    curl -LsSf https://astral.sh/uv/install.sh | sh"
    pip install -e ".[fast]"
fi

# 检查 spaCy 模型是否已安装
check_spacy_model() {
    local model=$1
    if command -v uv &> /dev/null; then
        PYTHONWARNINGS="ignore" uv run python -c "import spacy; spacy.load('$model')" 2>/dev/null
    else
        PYTHONWARNINGS="ignore" python3 -c "import spacy; spacy.load('$model')" 2>/dev/null
    fi
    return $?
}

# 下载 spaCy 英文模型
echo ""
if check_spacy_model "en_core_web_trf"; then
    echo "  ✓ 英文模型已安装 (en_core_web_trf)"
else
    echo "↓ 下载 spaCy 英文模型 (en_core_web_trf, ~440 MB)..."
    if command -v uv &> /dev/null; then
        PYTHONWARNINGS="ignore" uv run python -m spacy download en_core_web_trf 2>&1 | \
            grep -v "Requirement already satisfied" | \
            grep -E "(Downloading|Download and installation|✔|━)"
    else
        PYTHONWARNINGS="ignore" python3 -m spacy download en_core_web_trf 2>&1 | \
            grep -v "Requirement already satisfied" | \
            grep -E "(Downloading|Download and installation|✔|━)"
    fi
fi

# 下载 spaCy 瑞典语模型
echo ""
if check_spacy_model "sv_core_news_lg"; then
    echo "  ✓ 瑞典语模型已安装 (sv_core_news_lg)"
else
    echo "↓ 下载 spaCy 瑞典语模型 (sv_core_news_lg, ~545 MB)..."
    if command -v uv &> /dev/null; then
        PYTHONWARNINGS="ignore" uv run python -m spacy download sv_core_news_lg 2>&1 | \
            grep -v "Requirement already satisfied" | \
            grep -E "(Downloading|Download and installation|✔|━)"
    else
        PYTHONWARNINGS="ignore" python3 -m spacy download sv_core_news_lg 2>&1 | \
            grep -v "Requirement already satisfied" | \
            grep -E "(Downloading|Download and installation|✔|━)"
    fi
fi

# HanLP 提示
echo ""
echo "i HanLP 中文模型会在首次使用时自动下载 (~400 MB)"

# 完成
echo ""
echo "=================================================="
echo "  ✓ 安装完成！"
echo "=================================================="
echo ""
echo "磁盘空间使用:"
echo "  - spaCy 英文模型: ~440 MB"
echo "  - spaCy 瑞典语模型: ~545 MB"
echo "  - HanLP 中文模型: ~400 MB (首次使用时下载)"
echo "  - 总计: ~1.4 GB"
echo ""
echo "内存占用:"
echo "  - 按需加载: 同时只加载一个语言模型 (~1.5-1.8 GB)"
echo "  - 不会同时占用 4-5 GB 内存"
echo ""
echo "运行测试:"
echo "  python3 scripts/test_fast_extractor.py"
echo ""
