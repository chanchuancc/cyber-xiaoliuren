import base64
import json
import subprocess

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

# --- Push to Meihua ---
repo_meihua = "chanchuancc/cyber-meihuayishu"
upload_to_github("meihua_app.py", open("meihua_app.py").read(), "Update: Imperial Portal UI v1.6.0", repo_meihua)
upload_to_github("meihua_data.py", open("meihua_data.py").read(), "Update: Core data", repo_meihua)
upload_to_github("requirements.txt", open("requirements.txt").read(), "Update: Requirements", repo_meihua)

# --- Push to Xiaoliuren ---
repo_xiao = "chanchuancc/cyber-xiaoliuren"
upload_to_github("app.py", open("app.py").read(), "Update: Imperial Portal UI v1.6.0", repo_xiao)
upload_to_github("requirements.txt", open("requirements.txt").read(), "Update: Requirements", repo_xiao)
