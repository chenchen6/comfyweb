import os
import json
import requests
from fastapi.responses import HTMLResponse, FileResponse
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# 設定路徑
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOW_PATH = os.path.join(BASE_DIR, "workflows", "fastapi_api.json")
COMFY_API_URL = "http://127.0.0.1:8188/prompt"
HTML_PATH = os.path.join(BASE_DIR, "frontend", "index.html")
COMFY_OUTPUT_PATH = r"C:/UserPath/ComfyUI/output"

class DrawRequest(BaseModel):
    prompt_text: str

@app.get("/", response_class=HTMLResponse)
def read_index():
    # 讀取你的 HTML 檔案內容
    with open(HTML_PATH, "r", encoding="utf-8") as f:
        return f.read()

@app.post("/draw")
def draw_image(request: DrawRequest):
    with open(WORKFLOW_PATH, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # 更全面的檢查邏輯
    node_id = "13"
    if node_id in workflow:
        # 直接賦值，不進行多餘的 if 檢查
        workflow[node_id]["inputs"]["value"] = request.prompt_text
        print(f">>> [確認修改] 節點 #{node_id} 的內容已變更為: {request.prompt_text}")
    else:
        print(f"!!! 找不到節點 #{node_id}")
    
    import random
    workflow["2"]["inputs"]["seed"] = random.randint(1, 100000000000000)
    
    payload = {"prompt": workflow}
    response = requests.post(COMFY_API_URL, json=payload)
    print(f"ComfyUI 回應狀態: {response.status_code}")
    return response.json()

@app.get("/check-status/{prompt_id}")
def check_status(prompt_id: str):
    # 向 ComfyUI 查詢歷史紀錄
    history_url = f"http://127.0.0.1:8188/history/{prompt_id}"
    response = requests.get(history_url)
    history = response.json()

    # 如果歷史紀錄裡有這個 ID，代表算完了
    if prompt_id in history:
        # 從 #11 號節點抓取圖片檔名
        outputs = history[prompt_id].get("outputs", {})
        if "11" in outputs:
            images = outputs["11"].get("images", [])
            if images:
                filename = images[0]["filename"]
                return {"status": "completed", "filename": filename}
    
    return {"status": "processing"}

@app.get("/get-image/{filename}")
def get_processed_image(filename: str):
    import os
    # 確保 filename 沒有多餘的空白
    file_path = os.path.join(COMFY_OUTPUT_PATH, filename.strip())
    
    # 診斷用：如果找不到圖，在終端機印出路徑
    if not os.path.exists(file_path):
        print(f"找不到檔案！嘗試路徑為: {file_path}")
        return {"error": "404 Not Found"}

    return FileResponse(file_path)
