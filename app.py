from flask import Flask, render_template, request, jsonify
from agents import extractor, planner, writer
from config import token_usage

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/sample_data/oral_history.txt")
def sample_data():
    import os
    path = os.path.join(os.path.dirname(__file__), "sample_data", "oral_history.txt")
    with open(path, "r", encoding="utf-8") as f:
        return f.read(), 200, {"Content-Type": "text/plain; charset=utf-8"}


@app.route("/api/process", methods=["POST"])
def process():
    data = request.get_json()
    text = data.get("text", "").strip()

    if not text:
        return jsonify({"error": "请输入口述历史文本"}), 400

    if len(text) < 100:
        return jsonify({"error": "文本太短，请输入至少100字的口述记录"}), 400

    try:
        # Agent 1: Extract events
        result1 = extractor.run(text)
        events = result1["events"]

        # Agent 2: Plan timeline
        result2 = planner.run(events, text)
        timeline = result2["timeline"]

        # Agent 3: Write biography
        result3 = writer.run(timeline, text)
        biography = result3["biography"]

        return jsonify({
            "timeline": timeline,
            "biography": biography,
            "token_usage": token_usage,
        })

    except Exception as e:
        return jsonify({"error": f"处理出错: {str(e)}"}), 500


@app.route("/api/token_usage")
def get_token_usage():
    return jsonify(token_usage)


if __name__ == "__main__":
    from config import LLM_MODEL, LLM_BASE_URL
    print(f"[启动] 使用模型: {LLM_MODEL} @ {LLM_BASE_URL}")
    app.run(debug=True, host="0.0.0.0", port=5000)
