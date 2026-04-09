import base64
import json
import subprocess
import os

def get_sha(path, repo):
    cmd = [
        "gh", "api",
        f"/repos/{repo}/contents/{path}"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        data = json.loads(stdout)
        return data.get("sha")
    return None

def upload_to_github(path, content, message, repo):
    sha = get_sha(path, repo)
    encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
    data = {
        "message": message,
        "content": encoded_content
    }
    if sha:
        data["sha"] = sha
        
    cmd = [
        "gh", "api",
        "--method", "PUT",
        f"/repos/{repo}/contents/{path}",
        "--input", "-"
    ]
    process = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate(input=json.dumps(data))
    if process.returncode == 0:
        print(f"Successfully uploaded {path} to {repo}")
    else:
        print(f"Failed to upload {path} to {repo}: {stderr}")

# --- Push to Both Repos ---
repos = ["chanchuancc/cyber-meihuayishu", "chanchuancc/cyber-xiaoliuren"]

for repo in repos:
    # 1. Main Apps
    if "meihua" in repo:
        upload_to_github("meihua_app.py", open("meihua_app.py").read(), "Update: Imperial Void UI v1.9.0", repo)
        upload_to_github("meihua_data.py", open("meihua_data.py").read(), "Update: Core data", repo)
    else:
        upload_to_github("app.py", open("app.py").read(), "Update: Imperial Void UI v1.9.0", repo)
    
    # 2. Config & Dependencies
    upload_to_github("requirements.txt", open("requirements.txt").read(), "Update: Requirements", repo)
    upload_to_github(".streamlit/config.toml", open(".streamlit/config.toml").read(), "Force Dark Theme Config", repo)
