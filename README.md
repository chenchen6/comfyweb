# comfyui-webui-test
ComfyUI到用戶端還傳圖片 side-project測試

## 流程拆解
本地ComfyUI(127.0.0.1:8188, 預設):算圖工廠
Fastapi:對街ComfyUI與WEB端呈現
HTML:供用戶操作

## 使用方法
用戶打上提示詞，等待ComfyUI運算圖片，完成後回傳圖片
