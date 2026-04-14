import os
import json
import random
import requests
from pathlib import Path

class ComfyBase:
    def __init__(self, workflows_dir, comfy_url, models_root=None):
        self.workflows_dir = workflows_dir
        self.comfy_url = comfy_url
        self.model_cache = {}
        if models_root:
            self.scan_models(models_root)

    def scan_models(self, base_path):
        print(f"📂 [DEBUG] 開始掃描模型根目錄: {base_path}")
        if not base_path or not os.path.exists(base_path):
            print(f"❌ [ERROR] 模型路徑不存在，請檢查 .env 的 COMFY_MODELS_PATH")
            return
        
        target_dirs = ["diffusion_models", "checkpoints", "clip", "vae", "loras", "text_encoders"]
        new_cache = {}
        
        for sub_dir in target_dirs:
            full_sub_path = os.path.join(base_path, sub_dir)
            if not os.path.exists(full_sub_path): 
                print(f"❌ [ERROR] 子目錄不存在: {full_sub_path}")
                continue
            
            for root, _, files in os.walk(full_sub_path):
                for f in files:
                    if f.endswith(('.safetensors', '.ckpt', '.pt')):
                        rel_path = os.path.relpath(os.path.join(root, f), full_sub_path)
                        new_cache[f] = rel_path.replace("/", "\\")
                        
        self.model_cache = new_cache
        print(f"✅ [DEBUG] 掃描完成，共計快取 {len(self.model_cache)} 個模型檔案")

    def get_model_path(self, model_name):
        pure_name = os.path.basename(model_name)
        if pure_name in self.model_cache:
            return self.model_cache[pure_name]
    
        print(f"⚠️ [WARN] 模型 '{pure_name}' 不在快取中，將使用原始路徑: {model_name}")
        return model_name

    def load_workflow(self, workflow_name):
        path = os.path.join(self.workflows_dir, workflow_name)
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def inject_common(self, workflow, cfg, prompt_text):
        # 1. 注入 Prompt (自動匹配多種 Key)
        p_id = cfg.get("prompt_node")
        if p_id in workflow:
            target = workflow[p_id]["inputs"]
            for key in ["String", "string", "text", "value"]:
                if key in target:
                    target[key] = prompt_text
                    print(f"🎯 [DEBUG] 成功將 Prompt 寫入節點 {p_id} 的 '{key}' 欄位")
                    break
        
        # 2. 注入 Seed
        s_id = cfg.get("seed_node")
        if s_id in workflow:
            workflow[s_id]["inputs"]["seed"] = random.randint(1, 10**14)

        # 3. 注入 Models
        model_map = cfg.get("models", {})
        for node_id, m_name in model_map.items():
            if node_id in workflow:
                corrected = self.get_model_path(m_name)
                inputs = workflow[node_id].get("inputs", {})
                for k, v in inputs.items():
                    if isinstance(v, str) and v.lower().endswith(('.safetensors', '.ckpt', '.pt')):
                        inputs[k] = corrected
                        break
        return workflow

    def send_request(self, workflow):
        return requests.post(self.comfy_url, json={"prompt": workflow}).json()