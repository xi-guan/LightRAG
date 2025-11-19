#!/bin/bash
# LightRAG Server 一键启动脚本（含三语言支持）

set -e

# 获取脚本所在目录
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

cd "$PROJECT_ROOT"

echo "======================================================================"
echo "  LightRAG Server 启动 (三语言实体提取器)"
echo "======================================================================"
echo ""

# 1. 检查 UV
echo "🔍 检查 UV..."
if ! command -v uv &> /dev/null; then
    echo "   ⚠️  UV 未安装，正在安装..."
    curl -LsSf https://astral.sh/uv/install.sh | sh
    export PATH="$HOME/.cargo/bin:$PATH"
else
    echo "   ✓ UV 已安装 ($(uv --version))"
fi

# 2. 检查依赖
echo ""
echo "🔍 检查依赖..."
if [ ! -d ".venv" ]; then
    echo "   正在安装依赖..."
    uv sync --extra api --extra trilingual
else
    echo "   ✓ 虚拟环境已存在"
fi

# 3. 检查模型
echo ""
echo "🔍 检查语言模型..."

MODEL_CHECK_PASSED=true

# 检查英文模型
if ! python3 -c "import spacy; spacy.load('en_core_web_trf')" 2>/dev/null; then
    echo "   ⚠️  英文模型未安装"
    MODEL_CHECK_PASSED=false
fi

# 检查瑞典语模型
if ! python3 -c "import spacy; spacy.load('sv_core_news_lg')" 2>/dev/null; then
    echo "   ⚠️  瑞典语模型未安装"
    MODEL_CHECK_PASSED=false
fi

if [ "$MODEL_CHECK_PASSED" = false ]; then
    echo ""
    echo "   正在下载语言模型..."
    ./scripts/install_trilingual_models.sh
else
    echo "   ✓ 所有语言模型已安装"
fi

# 4. 检查配置
echo ""
echo "🔍 检查配置文件..."
if [ ! -f "config/local.yaml" ]; then
    echo "   正在生成配置..."
    ./scripts/setup.sh
else
    echo "   ✓ 配置文件已存在"
fi

# 5. 启动服务器
echo ""
echo "======================================================================"
echo "  🚀 启动 LightRAG Server"
echo "======================================================================"
echo ""
echo "服务器地址: http://localhost:9621"
echo "健康检查: http://localhost:9621/health"
echo ""
echo "测试命令:"
echo "  - 自动测试: uv run python examples/test_server_trilingual.py"
echo "  - 手动测试: curl http://localhost:9621/health"
echo ""
echo "停止服务器: Ctrl+C"
echo ""
echo "======================================================================"
echo ""

# 启动服务器
uv run lightrag-server --host 0.0.0.0 --port 9621
