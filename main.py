from flask import Flask, request, jsonify
import openai
import requests
import time
import os

app = Flask(__name__)

# 环境变量读取方式（推荐安全）
OPENAI_API_KEY = os.environ.get("sk-proj-0fYh24w4PyMke6vOIt65ty3qGuJJsCObQbcoC08nTy5UnbPtmlMzNjsnTUy1SZC_syRihHo__VT3BlbkFJrCOsgaS6L3Fh1skfmTeva9YDG2YhoLoVBK4DVW0woJ5sEibyQUNS1ygMxq4-_kkYZpY_8Ql1kAsk-proj-0fYh24w4PyMke6vOIt65ty3qGuJJsCObQbcoC08nTy5UnbPtmlMzNjsnTUy1SZC_syRihHo__VT3BlbkFJrCOsgaS6L3Fh1skfmTeva9YDG2YhoLoVBK4DVW0woJ5sEibyQUNS1ygMxq4-_kkYZpY_8Ql1kA")
ELEVENLABS_API_KEY = os.environ.get("sk_b41fcfe0dc4bb5e7d7c99efbb3770d97a4edde8af16cddc7")
VOICE_ID = os.environ.get("Bp4JBv27FA0v7JZ4UXuw")

# ChatGPT回答
def get_gpt_response(prompt):
    try:
        headers = {
            "Authorization": f"Bearer {OPENAI_API_KEY}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": "gpt-3.5-turbo",
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7
        }
        res = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
        res.raise_for_status()  # 抛出 HTTP 错误
        return res.json()["choices"][0]["message"]["content"]
    except Exception as e:
        print("GPT错误：", e)
        return "对不起，我暂时无法回答。"

# ElevenLabs语音合成
def synthesize_speech(text):
    try:
        headers = {
            "xi-api-key": ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"
        payload = {
            "text": text,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {"stability": 0.5, "similarity_boost": 0.75}
        }
        res = requests.post(url, headers=headers, json=payload)
        res.raise_for_status()
        filename = f"audio_{int(time.time())}.mp3"
        filepath = os.path.join("static", filename)
        with open(filepath, "wb") as f:
            f.write(res.content)
        return f"/static/{filename}"
    except Exception as e:
        print("语音合成失败：", e)
        return ""

@app.route("/ask", methods=["POST"])
def ask():
    try:
        data = request.json
        user_input = data.get("message", "")
        if not user_input:
            return jsonify({"error": "缺少 message 参数"}), 400

        print("收到消息：", user_input)
        gpt_reply = get_gpt_response(user_input)
        audio_url = synthesize_speech(gpt_reply)

        return jsonify({"text": gpt_reply, "audio_url": audio_url})
    except Exception as e:
        print("服务器错误：", e)
        return jsonify({"error": "服务器内部错误", "detail": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)