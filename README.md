# ComfyUI-Web-Controller AI 繪圖實驗室
一個基於 FastAPI 的輕量化網頁控制台，將 ComfyUI 的強大 AI 算圖能力透過 API 轉化為直觀的 Web 介面

套件環境裝在comfyweb資料夾內，ComfyUI預設127.0.0.1:8188，可於本地直接運行

### 2026/04/14更新內容
本次更新針對系統架構進行了大規模重構，提升了程式碼的可維護性與擴充性：

* **新增 Image-to-Image (i2i) 功能**：
    * 支援上傳圖片並自動注入工作流。
    * 採用「檔案儲存至 Input 資料夾」並傳遞「檔名」至 ComfyUI 的標準做法，提升大圖傳輸的穩定性。
      
* **優化模型路徑適配性 (Fixed Model Path Logic)**：
    * 新增 `scan_models` 機制，自動遍歷模型根目錄。
    * 具備自動校正路徑功能，支援在 `config.json` 中僅填寫檔名即可自動對應子目錄層級。
    * 加入路徑偵錯 (Debug Log)，當路徑配置錯誤時會主動發出警告。
      
* **自行添加 Workflow 機制**：
    * 實現邏輯與配置分離，使用者僅需將新的 JSON 放入 `workflows` 資料夾，並在 `config.json` 註冊節點 ID 即可快速擴充功能。
    * 支援動態載入工作流清單，前端可自動更新選項。

### 核心特色
即時進度追蹤：內建自動化狀態監測，無需手動整理，系統將自動偵測繪圖進度並完成顯示。

動態參數注入：透過 FastAPI 接口即時修改工作流內容

自動圖片擷取：生成完成後自動從 ComfyUI output 目錄檢索並即時預覽。

自動隨機機制：每次請求自動生成隨機 seed，確保生成結果的多樣性。

輕量化架構：純 Python + HTML 實現，無需複雜的前端框架即可運行。

### 技術棧
* Backend: Python 3.10+, FastAPI, Uvicorn
* Frontend: JavaScript, HTML, CSS
* 核心整合: ComfyUI API 端口



### 專案結構
```

comfyweb/
├── frontend/               # 網頁控制台介面
│   └── index.html         
│   └── style.css
│   └── scripts.js
├── workflows/              # 匯出的 ComfyUI 工作流
│   └── config.json         #設定你工作流節點ID
│   └── text2image.json   
│   └── image2image.json
├── base.py
├── processors.py 
└── main.py                 # FastAPI 後端主程式

```

使用模型為

T2I workflow:
* diffusion model : BEYOND_REALITY_ZIMAGE.safetensors
* clip : qwen_3_4b.safetensors
* vae : UltraFlux-v1.safetensors
  
I2I workflow:
* diffusion model : qwen_image_edit_2511_fp8mixed.safetensors
* clip : qwen_2.5_vl_7b_fp8_scaled.safetensors
* vae : qwen_image_vae.safetensors
* loras : Qwen-Image-Edit-2511-Lightning-4steps-V1.0-bf16

### 運作流程

提交指令或圖片：使用者在網頁端輸入提詞/圖片。

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

* CMD 進入環境
  執行`uvicorn main:app --reload`，造訪 `http://127.0.0.1:8000`

* 開啟ComfyUI或編輯器的terminal，主要查看log追蹤進度，以及查看報錯

* input位置
  設定`.env`內的`COMFY_INPUT_PATH=C:\Your\Path\To\ComfyUI\input`
  
* models位置
  設定`.env`內的`COMFY_MODELS_PATH=C:\Your\Path\To\ComfyUI\models`，非常重要，否則抓取不到你的模型檔案
  
* output位置
  直接在網站上查看，需要時則直接儲存

### 展示
sample/1

![1](https://github.com/chenchen6/comfyui-webui-test/blob/main/sample/1.gif)

sample/2

![2](https://github.com/chenchen6/comfyui-webui-test/blob/main/sample/2.gif)
