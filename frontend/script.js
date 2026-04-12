// --- 1. 初始化：載入 Workflow 選單 ---
window.onload = async () => {
    try {
        const res = await fetch('/list-workflows');
        const data = await res.json();
        const select = document.getElementById('workflowSelect');
        if (!select) return; // 確保 HTML 有這個 ID
        
        select.innerHTML = ""; 
        data.workflows.forEach(name => {
            const option = document.createElement('option');
            option.value = name;
            option.textContent = name;
            select.appendChild(option);
        });
    } catch (e) {
        console.error("無法載入 Workflow 清單", e);
    }
};

function switchTab(event, tabName) {
    document.querySelectorAll('.tab-btn').forEach(btn => btn.classList.remove('active'));
    event.currentTarget.classList.add('active');
    document.querySelectorAll('.tab-content').forEach(content => content.classList.remove('active'));
    document.getElementById(`${tabName}-tab-content`).classList.add('active');
}

function previewImage(input) {
    const img = document.getElementById('resultImageI2i');
    if (input.files && input.files[0]) {
        const reader = new FileReader();
        reader.onload = (e) => {
            img.src = e.target.result;
            img.style.display = 'block';
        };
        reader.readAsDataURL(input.files[0]);
    }
}

// --- 2. 修改：發送請求 (統一使用 FormData 以配合後端) ---
async function sendPromptT2i() {
    const prompt = document.getElementById('promptInputT2i').value;
    const workflow = document.getElementById('workflowSelect').value;
    const status = document.getElementById('statusT2i');
    const img = document.getElementById('resultImageT2i');

    if (!prompt) return alert("請輸入提示詞！");

    status.innerHTML = '<p class="loading-spinner">發送中...</p>';
    
    const formData = new FormData();
    formData.append("workflow_name", workflow);
    formData.append("prompt_text", prompt);

    try {
        const response = await fetch('/draw', { method: 'POST', body: formData });
        const data = await response.json();
        startMonitoring(data.prompt_id, status, img, workflow);
    } catch (e) {
        status.innerHTML = `<p style="color:red;">失敗：${e.message}</p>`;
    }
}

async function sendPromptI2i() {
    const prompt = document.getElementById('promptInputI2i').value;
    const file = document.getElementById('imageInputI2i').files[0];
    const workflow = document.getElementById('workflowSelect').value;
    const status = document.getElementById('statusI2i');
    const img = document.getElementById('resultImageI2i');

    if (!file) return alert("請先上傳圖片！");

    status.innerHTML = '<p class="loading-spinner">處理中...</p>';

    const formData = new FormData();
    formData.append("workflow_name", workflow);
    formData.append("prompt_text", prompt || "semi-realistic anime style");
    formData.append("file", file);

    try {
        const response = await fetch('/draw', { method: 'POST', body: formData });
        const data = await response.json();
        startMonitoring(data.prompt_id, status, img, workflow);
    } catch (e) {
        status.innerHTML = `<p style="color:red;">連線失敗：${e.message}</p>`;
    }
}

// --- 3. 修改：監測邏輯 (改用 Base64 顯示) ---
function startMonitoring(promptId, statusElement, imgElement, workflowName) {
    if (!promptId) {
        statusElement.innerHTML = '<p style="color:red;">錯誤：未取得 ID</p>';
        return;
    }

    const checkInterval = setInterval(async () => {
        try {
            const statusRes = await fetch(`/check-status/${promptId}?workflow_name=${workflowName}`);
            const statusData = await statusRes.json();

            if (statusData.status === "completed") {
                clearInterval(checkInterval);
                statusElement.innerHTML = '<p style="color: green;">完成！</p>';
                
                // 💡 關鍵修改：直接使用回傳的 image_data (Base64)
                imgElement.src = `data:image/png;base64,${statusData.image_data}`;
                imgElement.style.display = 'block';
            } else if (statusData.status === "processing") {
                statusElement.innerHTML = '<p class="loading-spinner">AI 繪製中...</p>';
            } else {
                // 處理 error 情況
                clearInterval(checkInterval);
                statusElement.innerHTML = `<p style="color:red;">${statusData.msg || '發生錯誤'}</p>`;
            }
        } catch (err) {
            console.error("監測失敗:", err);
        }
    }, 2000);
}