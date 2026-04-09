import json
import base64

with open("app.py", "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "message": "style: 陛下亲裁 - 视觉大重构 v1.2.0 (去冗余、正中宫、提天机)",
    "content": content,
    "sha": "bf8fbc6a473c0ff688a97cf4e6370bb27abf8368"
}

with open("payload.json", "w") as f:
    json.dump(payload, f)
