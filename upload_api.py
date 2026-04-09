import base64
import json
import subprocess

def get_sha(path):
    cmd = [
        "gh", "api",
        f"/repos/chanchuancc/cyber-xiaoliuren/contents/{path}"
    ]
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    stdout, stderr = process.communicate()
    if process.returncode == 0:
        data = json.loads(stdout)
        return data.get("sha")
    return None

def upload_to_github(path, content, message, repo="chanchuancc/cyber-meihuayishu"):
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

files = {
    "meihua_app.py": "Initial Meihua Yi Shu app",
    "meihua_data.py": "Meihua core data dictionary",
    "requirements.txt": "Dependency list for Meihua"
}

for filename, msg in files.items():
    try:
        with open(filename, 'r') as f:
            content = f.read()
            upload_to_github(filename, content, msg)
    except Exception as e:
        print(f"Error reading {filename}: {e}")
