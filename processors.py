import os
import random
from base import ComfyBase

class T2IProcessor(ComfyBase):
    def run(self, workflow_name, prompt_text, cfg):
        workflow = self.load_workflow(workflow_name)
        workflow = self.inject_common(workflow, cfg, prompt_text)
        return self.send_request(workflow)

class I2IProcessor(ComfyBase):
    def __init__(self, workflows_dir, comfy_url, input_path, models_root):
        super().__init__(workflows_dir, comfy_url, models_root)
        self.input_path = input_path

    async def run(self, workflow_name, prompt_text, file, cfg):
        workflow = self.load_workflow(workflow_name)
        
        # 處理圖片上傳
        i_id = cfg.get("image_node")
        if i_id and i_id in workflow and file:
            os.makedirs(self.input_path, exist_ok=True)
            
            save_name = f"api_{random.randint(100,999)}_{file.filename}"
            save_path = os.path.join(self.input_path, save_name)
            print(f"📂 [I2I DEBUG] 圖片存檔路徑: {os.path.abspath(save_path)}")
            
            content = await file.read()
            with open(save_path, "wb") as f:
                f.write(content)
            
            workflow[i_id]["inputs"]["image"] = save_name
            print(f"📸 I2I 圖片已就緒: {save_name}")

        workflow = self.inject_common(workflow, cfg, prompt_text)
        return self.send_request(workflow)