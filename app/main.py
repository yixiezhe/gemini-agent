import os
import subprocess
import google.generativeai as genai
from flask import Flask, request, jsonify

app = Flask(__name__)

# --- 安全提示 ---
# 在生产环境中，执行来自 AI 的任意代码非常危险。
# 这里的实现仅为演示目的。请务必增加安全校验和限制。

# 从环境变量中读取你的 Google AI API Key
# 建议使用 .env 文件或 Docker 的 secrets 管理
genai.configure(api_key="AIzaSyDAz-8VSxbHNCzykRq9gJwAI-ANRvI-2bc") # 替换成你的 API Key

# 初始化 Gemini 模型
model = genai.GenerativeModel('gemini-pro') # 或者 gemini-pro

# 定义工作目录 (这是在容器内的路径)
PROJECT_DIR = "/workspace"

@app.route('/ask', methods=['POST'])
def ask_gemini():
    data = request.json
    prompt = data.get('prompt')

    if not prompt:
        return jsonify({"error": "Prompt is required"}), 400

    try:
        # 在 prompt 中加入上下文信息，让 Gemini 知道它可以做什么
        full_prompt = f"""
        你是一个 AI 编程助手，部署在 Linux Docker 容器中。
        你可以访问位于 '{PROJECT_DIR}' 目录下的项目文件。
        你可以通过特定的格式来响应，以执行文件操作或 shell 命令。

        可用指令格式:
        - 读取文件: <READ_FILE>path/to/file.txt</READ_FILE>
        - 写入文件: <WRITE_FILE path="path/to/file.ext">file content here</WRITE_FILE>
        - 执行命令: <EXEC>your_shell_command_here</EXEC>

        用户的请求是: {prompt}
        """

        response = model.generate_content(full_prompt)

        # 这里可以添加解析 response.text 并执行指令的逻辑
        # 为简化，我们直接返回 Gemini 的原始文本
        # 一个更高级的实现会在这里解析 <EXEC> 等标签并执行

        return jsonify({"response": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 增加一个执行命令的端点（需要非常小心！） ---
@app.route('/execute', methods=['POST'])
def execute_command():
    data = request.json
    command = data.get('command')

    if not command:
        return jsonify({"error": "Command is required"}), 400

    try:
        # 安全警告：直接执行外部命令有严重风险！
        # 这里的 cwd 设置让命令在项目目录中执行
        result = subprocess.run(
            command, 
            shell=True, 
            capture_output=True, 
            text=True, 
            cwd=PROJECT_DIR,
            check=True # 如果命令失败则抛出异常
        )
        return jsonify({
            "stdout": result.stdout,
            "stderr": result.stderr,
            "returncode": result.returncode
        })
    except subprocess.CalledProcessError as e:
         return jsonify({
            "error": "Command failed",
            "stdout": e.stdout,
            "stderr": e.stderr,
            "returncode": e.returncode
        }), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
