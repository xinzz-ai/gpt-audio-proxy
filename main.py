from flask import Flask, request, jsonify
import openai
import requests
import time

app = Flask(__name__)

# 替换为你的真实 API key
OPENAI_API_KEY = "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"
ELEVENLABS_API_KEY = "sk_b41fcfe0dc4bb5e7d7c99efbb3770d97a4edde8af16cddc7"
VOICE_ID = "Bp4JBv27FA0v7JZ4UXuw"  # 可选：你的声音模型ID

# ChatGPT回答
def get_gpt_response(prompt):
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
    return res.json()["choices"][0]["message"]["content"]

# ElevenLabs语音合成
def synthesize_speech(text):
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
    filename = f"audio_{int(time.time())}.mp3"
    with open(f"static/{filename}", "wb") as f:
        f.write(res.content)
    return f"/static/{filename}"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    user_input = data.get("message", "")
    print(f"收到消息: {user_input}")

    gpt_reply = get_gpt_response(user_input)
    audio_url = synthesize_speech(gpt_reply)

    return jsonify({"text": gpt_reply, "audio_url": audio_url})

import os

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)