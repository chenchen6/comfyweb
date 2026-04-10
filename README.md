# ComfyUI-Web-Controller AI 繪圖實驗室
一個基於 FastAPI 的輕量化網頁控制台，將 ComfyUI 的強大 AI 算圖能力透過 API 轉化為直觀的 Web 介面。

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
├── frontend/
│   └── index.html         # 網頁控制台介面
├── workflows/
│   └── fastapi_api.json   # 匯出的 ComfyUI 工作流 (API 格式)
└── comfyweb.py            # FastAPI 後端主程式
```

### 運作流程
提交指令：使用者在網頁端輸入提詞。

數據封裝：後端更新工作流 JSON，設定提詞與隨機種子，並推送至 ComfyUI。

狀態同步：前端自動與後端通訊，追蹤該任務的執行狀態。

結果展示：一旦確認完成，系統自動加載生成的影像至網頁中央。
