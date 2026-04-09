import json
import base64

with open("meihua/requirements.txt", "rb") as f:
    content = base64.b64encode(f.read()).decode("utf-8")

payload = {
    "message": "fix: 完善依赖配置",
    "content": content,
    "sha": "13986d1041f1a1de1d53177c6a7be3f294111e7b"
}

with open("req_payload.json", "w") as f:
    json.dump(payload, f)
