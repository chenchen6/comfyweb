# ComfyUI-Web-Controller AI 繪圖實驗室
一個基於 FastAPI 的輕量化網頁控制台，將 ComfyUI 的強大 AI 算圖能力透過 API 轉化為直觀的 Web 介面

套件環境裝在comfyweb資料夾內，ComfyUI預設127.0.0.1:8188，可於本地直接運行

### 核心特色
即時進度追蹤：內建自動化狀態監測，無需手動整理，系統將自動偵測繪圖進度並完成顯示。

動態參數注入：透過 FastAPI 接口即時修改工作流內容

自動圖片擷取：生成完成後自動從 ComfyUI output 目錄檢索並即時預覽。

自動隨機機制：每次請求自動生成隨機 seed，確保生成結果的多樣性。

輕量化架構：純 Python + HTML 實現，無需複雜的前端框架即可運行。

### 技術棧
* Backend: Python 3.10+, FastAPI, Uvicorn
* Frontend: JavaScript, HTML, CSS
* 核心整合: ComfyUI API 接口實作



### 專案結構
```
comfyweb/
├── frontend/              # 網頁控制台介面
│   └── index.html         
│   └── style.css
│   └── script.js 
├── workflows/             # 匯出的 ComfyUI 工作流 (API 格式)
│   └── fastapi_api.json   
│   └── image2image.json
└── comfyui_fastapi.py     # FastAPI 後端主程式
```

使用模型為

* diffusion model:BEYOND_REALITY_ZIMAGE.safetensors
* clip:qwen_3_4b.safetensors
* vae:UltraFlux-v1.safetensors

### 運作流程
提交指令：使用者在網頁端輸入提詞。

數據封裝：後端更新工作流 JSON，設定提詞與隨機種子，並推送至 ComfyUI。

狀態同步：前端自動與後端通訊，追蹤該任務的執行狀態。

結果展示：一旦確認完成，系統自動加載生成的影像至網頁中央。

### 配置與運行
啟動ComfyUI（default為 http://127.0.0.1:8188）

虛擬環境測試時為`/fast_api python=3.1X(依據想要的版本)`，安裝在comfyweb原生目錄內，亦可安裝至本地環境

```
pip install fastapi uvicorn requests
```
### 運行專案
* CMD 進入conda環境
  執行`uvicorn comfyui_fastapi:app --reload`，造訪 `http://127.0.0.1:8000`

* 開啟ComfyUI，主要查看log追蹤進度，以及查看報錯
  
* output位置
  在`comfyui_fastapi.py`中`COMFY_OUTPUT_PATH = r"C:/UserPath/ComfyUI/output"`

記得更換成自身ComfyUI/output的PATH

### 展示
sample/1

![1](https://github.com/chenchen6/comfyui-webui-test/blob/main/sample/1.gif)

sample/2

![2](https://github.com/chenchen6/comfyui-webui-test/blob/main/sample/2.gif)
