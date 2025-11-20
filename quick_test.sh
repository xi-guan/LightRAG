#!/bin/bash
# 快速测试脚本 - 直接上传文档到 LightRAG

SERVER_URL="http://localhost:9621"

echo "======================================================================"
echo "  LightRAG 快速测试"
echo "======================================================================"
echo ""

# 检查服务器是否运行
echo "🔍 检查服务器状态..."
if ! curl -s "${SERVER_URL}/health" > /dev/null 2>&1; then
    echo "❌ 服务器未运行"
    echo ""
    echo "请先启动服务器："
    echo "  ./scripts/start_server_with_trilingual.sh"
    echo ""
    exit 1
fi

echo "✓ 服务器正在运行"
echo ""

# 显示服务器配置
echo "📋 服务器配置："
curl -s "${SERVER_URL}/health" | jq -r '.configuration | "  - 三语言提取器: \(.use_trilingual_extractor // "未配置")"'
echo ""

# 上传测试文档
echo "📤 上传测试文档..."
echo ""

# 中文文档
echo "1️⃣  中文文档："
echo "   内容: 腾讯公司由马化腾创立于1998年，总部位于深圳。"
RESPONSE=$(curl -s -X POST "${SERVER_URL}/documents/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "腾讯公司由马化腾创立于1998年，总部位于深圳。阿里巴巴由马云创立于1999年，总部位于杭州。"
  }')

STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "success" ]; then
    echo "   ✓ 上传成功"
else
    echo "   ✗ 上传失败: $RESPONSE"
fi
echo ""

# 英文文档
echo "2️⃣  英文文档："
echo "   内容: Apple Inc. was founded by Steve Jobs..."
RESPONSE=$(curl -s -X POST "${SERVER_URL}/documents/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apple Inc. was founded by Steve Jobs in 1976. Microsoft was founded by Bill Gates in 1975.",
    "language": "en"
  }')

STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "success" ]; then
    echo "   ✓ 上传成功"
else
    echo "   ✗ 上传失败: $RESPONSE"
fi
echo ""

# 瑞典语文档
echo "3️⃣  瑞典语文档："
echo "   内容: Spotify grundades av Daniel Ek..."
RESPONSE=$(curl -s -X POST "${SERVER_URL}/documents/insert" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Spotify grundades av Daniel Ek och Martin Lorentzon i Stockholm 2006.",
    "language": "sv"
  }')

STATUS=$(echo "$RESPONSE" | jq -r '.status')
if [ "$STATUS" = "success" ]; then
    echo "   ✓ 上传成功"
else
    echo "   ✗ 上传失败: $RESPONSE"
fi
echo ""

echo "======================================================================"
echo "  ✅ 测试完成"
echo "======================================================================"
echo ""
echo "提示："
echo "  - 查看服务器日志观察实体提取过程"
echo "  - 使用 curl 命令手动测试："
echo "    curl -X POST http://localhost:9621/documents/insert \\"
echo "      -H 'Content-Type: application/json' \\"
echo "      -d '{\"text\": \"你的文本\"}'"
echo ""
