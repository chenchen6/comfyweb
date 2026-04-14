import json
import os
import requests
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.staticfiles import StaticFiles
from dotenv import load_dotenv
from processors import T2IProcessor, I2IProcessor

load_dotenv()
app = FastAPI()

# 路徑與配置
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKFLOWS_DIR = os.path.join(BASE_DIR, "workflows")
COMFY_URL = "http://127.0.0.1:8188/prompt"
INPUT_PATH = os.getenv("comfy_input_path")
MODELS_PATH = os.getenv("COMFY_MODELS_PATH")

# 初始化處理器
t2i_handler = T2IProcessor(WORKFLOWS_DIR, COMFY_URL, MODELS_PATH)
i2i_handler = I2IProcessor(WORKFLOWS_DIR, COMFY_URL, INPUT_PATH, MODELS_PATH)

def get_config(name):
    path = os.path.join(WORKFLOWS_DIR, "config.json")
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
        return data.get("workflows", {}).get(name, {})

@app.get("/list-workflows")
def list_workflows():
    if not os.path.exists(WORKFLOWS_DIR):
        os.makedirs(WORKFLOWS_DIR)
    files = [f for f in os.listdir(WORKFLOWS_DIR) if f.endswith('.json')]
    files = [f for f in files if f != "config.json"]
    return {"workflows": files}

@app.post("/draw")
async def draw(
    workflow_name: str = Form(...),
    prompt_text: str = Form(...),
    file: UploadFile = File(None)
):
    cfg = get_config(workflow_name)
    
    # 邏輯分流
    if cfg.get("image_node") or "image2image" in workflow_name:
        return await i2i_handler.run(workflow_name, prompt_text, file, cfg)
    return t2i_handler.run(workflow_name, prompt_text, cfg)

@app.get("/check-status/{prompt_id}")
def check_status(prompt_id: str, workflow_name: str):
    history_url = f"http://127.0.0.1:8188/history/{prompt_id}"
    response = requests.get(history_url)

    if response.status_code != 200: 
        return {"status": "error", "msg": "ComfyUI 無回應"}
    
    history = response.json()
    
    if prompt_id in history:
        outputs = history[prompt_id].get("outputs", {})
        cfg = get_config(workflow_name)
        out_id = cfg.get("output_node")
        
        print(f"🔍 [DEBUG] 正在檢查輸出節點 ID: {out_id}")

        if out_id and out_id in outputs:
            base64_data_list = outputs[out_id].get("text", [])
            if base64_data_list:
                print("✅ [DEBUG] 成功抓取到 Base64 字串")
                return {"status": "completed", "image_data": base64_data_list[0]}
            else:
                print("⚠️ [DEBUG] 找不到 'text' 欄位，請檢查輸出節點是否為 Base64 節點")
                
    return {"status": "processing"}

app.mount("/", StaticFiles(directory="frontend", html=True), name="static")