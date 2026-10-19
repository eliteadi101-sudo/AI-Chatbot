import os
from flask import Flask, request, jsonify, render_template
import requests
app=Flask(__name__)
API_KEY=os.getenv("AI_API_KEY","")
API_URL=os.getenv("AI_API_URL","https://api.openai.com/v1/chat/completions")
MODEL=os.getenv("AI_MODEL","gpt-4o-mini")
@app.get("/")
def home(): return render_template("index.html")
@app.post("/api/chat")
def chat():
    data=request.get_json(force=True); messages=data.get("messages",[])
    if not isinstance(messages,list) or len(messages)>30: return jsonify(error="Invalid message history"),400
    if not messages or not isinstance(messages[-1].get("content"),str): return jsonify(error="Please send a message"),400
    if not API_KEY:
        return jsonify(reply="Demo mode: add AI_API_KEY to your environment to connect a real model. You said: "+messages[-1]["content"])
    try:
        r=requests.post(API_URL,headers={"Authorization":f"Bearer {API_KEY}","Content-Type":"application/json"},
          json={"model":MODEL,"messages":[{"role":"system","content":"You are a concise, helpful assistant."}]+messages[-20:]},timeout=45)
        r.raise_for_status(); reply=r.json()["choices"][0]["message"]["content"]
        return jsonify(reply=reply)
    except (requests.RequestException,KeyError,ValueError) as e:
        return jsonify(error="AI provider request failed. Check the endpoint, key, and model."),502
if __name__=="__main__": app.run(debug=True)
