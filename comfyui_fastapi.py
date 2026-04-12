import os
import json
import requests
import random
import base64
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

app = FastAPI()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")
COMFY_URL = "http://127.0.0.1:8188/prompt"

# --- 核心：查表函式 ---
def get_workflow_config(workflow_name):
    config_path = os.path.join(WORKFLOWS_DIR, "config.json")
    if os.path.exists(config_path):
        with open(config_path, "r", encoding="utf-8") as f:
            full_config = json.load(f)
            # 回傳該工作流的設定，若沒設定則回傳空字典
            return full_config.get(workflow_name, {})
    return {}

@app.get("/list-workflows")
def list_workflows():
    if not os.path.exists(WORKFLOWS_DIR):
        os.makedirs(WORKFLOWS_DIR)
    files = [f for f in os.listdir(WORKFLOWS_DIR) if f.endswith('.json')]
    # 過濾掉 config.json 本身，只列出工作流
    files = [f for f in files if f != "config.json"]
    return {"workflows": files}

@app.post("/draw")
async def draw(
    workflow_name: str = Form(...),
    prompt_text: str = Form(...),
    file: UploadFile = File(None)
):
    # 1. 讀取 JSON 工作流
    json_path = os.path.join(WORKFLOWS_DIR, workflow_name)
    with open(json_path, "r", encoding="utf-8") as f:
        workflow = json.load(f)

    # 2. 獲取該工作流專屬的孔位配置 (DB 邏輯)
    cfg = get_workflow_config(workflow_name)
    p_id = cfg.get("prompt_node")
    s_id = cfg.get("seed_node")
    i_id = cfg.get("image_node")

    # 3. 注入圖片 (使用配置的 i_id)
    if i_id and i_id in workflow and file:
        img_data = await file.read()
        base64_str = base64.b64encode(img_data).decode('utf-8')

        log_preview = f"{base64_str[:50]} ... {base64_str[-50:]}"
        print("-" * 30)
        print(f"📸 圖片注入成功 (節點編號: {i_id})")
        print(f"📊 字串總長度: {len(base64_str)} 字元")
        print(f"📝 字串預覽: {log_preview}")
        print("-" * 30)
        
        target_node = workflow[i_id]["inputs"]
        if "string" in target_node:
            target_node["string"] = base64_str
        else:
            target_node["value"] = base64_str
        
        print(f"成功將圖片轉換為 Base64 並注入節點 {i_id}")

    # 4. 注入文字 (使用配置的 p_id)
    if p_id and p_id in workflow:
        # 這裡做個小相容：有些節點用 text，有些用 value
        if "text" in workflow[p_id]["inputs"]:
            workflow[p_id]["inputs"]["text"] = prompt_text
        else:
            workflow[p_id]["inputs"]["value"] = prompt_text

    # 5. 注入種子 (使用配置的 s_id)
    if s_id and s_id in workflow:
        workflow[s_id]["inputs"]["seed"] = random.randint(1, 10**14)

    # 6. 送出請求
    res = requests.post(COMFY_URL, json={"prompt": workflow})
    return res.json()

@app.get("/check-status/{prompt_id}")
def check_status(prompt_id: str, workflow_name: str): # 這裡要多收一個參數
    history_url = f"http://127.0.0.1:8188/history/{prompt_id}"
    response = requests.get(history_url)

    if response.status_code == 200:
        history = response.json()
    else:
        return {"status": "error", "msg": "ComfyUI 沒反應"}

    if prompt_id in history:
        outputs = history[prompt_id].get("outputs", {})
        
        # 7. 根據配置尋找輸出孔位 (Base64 字串的位置)
        cfg = get_workflow_config(workflow_name)
        out_id = cfg.get("output_node", "16") # 預設為 16
        
        if out_id in outputs:
            base64_data_list = outputs[out_id].get("text", [])
            if base64_data_list:
                return {
                    "status": "completed", 
                    "image_data": base64_data_list[0] 
                }
                
    return {"status": "processing"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")