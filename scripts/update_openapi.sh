#!/bin/bash

# 脚本: update_openapi.sh
# 描述: 自动启动 FastAPI 应用，生成最新的 OpenAPI 规约，并将其保存到 specs/openapi.json。

# --- 配置 ---
# 设置脚本在项目根目录下执行，无论从哪里调用它
cd "$(dirname "$0")/.."

HOST="127.0.0.1"
PORT="8001"
OPENAPI_URL="http://${HOST}:${PORT}/openapi.json"
OUTPUT_FILE="specs/openapi.json"
# ---

echo "🚀 准备更新 OpenAPI 规约..."

# 检查 uvicorn 是否可用
if ! command -v uvicorn &> /dev/null
then
    echo "❌ 错误: 'uvicorn' 命令未找到。请确保您已激活项目的虚拟环境。"
    exit 1
fi

# 1. 启动 FastAPI 服务 (后台运行)
echo "🔄 正在后台启动服务 (uvicorn api.server:app)..."
uvicorn api.server:app --host ${HOST} --port ${PORT} &
UVICORN_PID=$!

# 添加一个退出陷阱，确保即使脚本被中断，uvicorn 进程也能被清理
trap 'echo "🛑 捕获到退出信号，正在清理..."; kill $UVICORN_PID; exit' SIGINT SIGTERM

# 2. 等待服务启动
echo "⏳ 等待服务启动 (最多10秒)..."
for i in {1..10}; do
    # 使用 curl 的静默模式和连接超时来检查服务是否响应
    if curl -s --connect-timeout 1 ${OPENAPI_URL} > /dev/null; then
        echo "✅ 服务已在 ${OPENAPI_URL} 启动。"
        break
    fi
    # 如果循环结束仍未成功，则提示
    if [ $i -eq 10 ]; then
        echo "❌ 错误：服务在10秒内未能启动！"
        kill $UVICORN_PID
        exit 1
    fi
    sleep 1
done

# 3. 获取 OpenAPI JSON
echo "📥 正在从 ${OPENAPI_URL} 下载规约..."
if ! curl -s ${OPENAPI_URL} -o ${OUTPUT_FILE}; then
    echo "❌ 错误：下载 OpenAPI 规约失败！"
    kill $UVICORN_PID
    exit 1
fi

# 4. 停止服务
echo "🛑 正在停止服务 (PID: ${UVICORN_PID})..."
kill $UVICORN_PID
# 等待进程完全终止
wait $UVICORN_PID 2>/dev/null

# 5. 格式化 JSON 文件
echo "🎨 正在格式化 ${OUTPUT_FILE}..."
# 创建一个临时文件来存储格式化后的内容
TEMP_FILE=$(mktemp)
if python -m json.tool ${OUTPUT_FILE} > ${TEMP_FILE}; then
    mv ${TEMP_FILE} ${OUTPUT_FILE}
    echo "🎉 OpenAPI 规约已成功更新并格式化！"
else
    echo "⚠️ 警告：JSON 格式化失败，但规约文件已更新。"
    rm -f ${TEMP_FILE}
fi

echo "✨ 操作完成。"
exit 0
