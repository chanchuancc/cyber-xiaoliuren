import json
import base64

with open("meihua/meihua_app.py", "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "message": "feat: 陛下亲裁 - 梅花易数 v1.5.0 (神谕入口 Oracle Portal)",
    "content": content,
    "sha": "f6f217beffb0bba1d8395a9fed8426e328cf1af5"
}

with open("meihua_payload.json", "w") as f:
    json.dump(payload, f)
