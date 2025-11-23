#!/bin/bash
# LightRAG 配置初始化脚本
# 从 config.schema.yaml 自动生成 config/local.yaml 和 .env

set -e  # 遇到错误立即退出

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

echo "======================================================================"
echo "  LightRAG 配置初始化"
echo "======================================================================"
echo ""

# 检查 Python 版本
echo "→ 检查 Python 环境..."
if ! command -v python3 &> /dev/null; then
    echo "✗ 错误: 未找到 python3"
    echo "  请先安装 Python 3.7 或更高版本"
    exit 1
fi

python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "  Python 版本: $python_version"

# 确定使用的 Python 命令
if command -v uv &> /dev/null; then
    PYTHON_CMD="uv run python"
else
    PYTHON_CMD="python3"
fi

# 检查必要的 Python 包
echo ""
echo "→ 检查 Python 依赖..."
if ! $PYTHON_CMD -c "import yaml" 2>/dev/null; then
    echo "  ! 未找到 PyYAML，正在安装..."
    if command -v uv &> /dev/null; then
        uv pip install pyyaml
    else
        python3 -m pip install pyyaml
    fi
else
    echo "  ✓ PyYAML 已安装"
fi

# 检查 Schema 文件
echo ""
echo "→ 检查配置 Schema..."
SCHEMA_FILE="${PROJECT_ROOT}/config/config.schema.yaml"
if [ ! -f "$SCHEMA_FILE" ]; then
    echo "✗ 错误: 未找到 $SCHEMA_FILE"
    exit 1
fi
echo "  ✓ Schema 文件存在: config/config.schema.yaml"

# 生成 config/local.yaml
echo ""
echo "→ 生成本地配置..."
$PYTHON_CMD "${SCRIPT_DIR}/lib/generate_from_schema.py"

# 检查生成是否成功
if [ ! -f "${PROJECT_ROOT}/config/local.yaml" ]; then
    echo "✗ 错误: config/local.yaml 生成失败"
    exit 1
fi

# 生成 .env
echo ""
echo "→ 生成环境变量..."
$PYTHON_CMD "${SCRIPT_DIR}/lib/generate_env.py"

# 检查生成是否成功
if [ ! -f "${PROJECT_ROOT}/.env" ]; then
    echo "✗ 错误: .env 生成失败"
    exit 1
fi

echo ""
echo "======================================================================"
echo "  ✓ 配置初始化完成"
echo "======================================================================"
echo ""
echo "生成的文件:"
echo "  - config/local.yaml  (本地配置文件)"
echo "  - .env               (环境变量文件)"
echo ""

# Check if trilingual extractor is enabled
if grep -q "use_trilingual.*true" config/local.yaml 2>/dev/null || \
   grep -q "LIGHTRAG_ENTITY_EXTRACTION_USE_TRILINGUAL=true" .env 2>/dev/null; then
    echo "! 快速实体提取器已启用 (HanLP/spaCy)"
    echo "  请确保已安装依赖和模型:"
    echo "  ./scripts/install_fast_models.sh"
    echo ""
fi

echo "下一步:"
echo "  1. 安装依赖: uv sync --extra fast"
echo "  2. 下载模型: ./scripts/install_fast_models.sh  (如果启用快速提取)"
echo "  3. 启动服务: uv run lightrag-server"
echo ""
echo "提示:"
echo "  - 快速提取: 在 config/local.yaml 设置 use_trilingual: true (8-15x 速度)"
echo "  - LLM 提取: 设置 use_trilingual: false (默认，支持所有语言)"
echo "  - 这两个文件已添加到 .gitignore，不会提交到 Git"
echo ""
