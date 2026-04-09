import json
import base64

with open("meihua/meihua_app.py", "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "message": "style: 陛下亲裁 - 梅花易数 v1.2.0 (金曜视觉、落梅动效、正中宫)",
    "content": content,
    "sha": "f39a38dd0fa73d0ff1ef1042cd17425fdb628ecf"
}

with open("meihua_payload.json", "w") as f:
    json.dump(payload, f)
