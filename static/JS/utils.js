// ============ Pop Up Dialog ============
const dialogs = {
    login: document.querySelector(".login-dialog"),
    signup: document.querySelector(".signup-dialog")
}

document.querySelectorAll(".dialog__switch").forEach(btn=>{
    btn.addEventListener("click",(e)=>{
        e.preventDefault()

        // 抓取目前開啟的 dialog 是哪個
        const currentDialog = btn.closest(".dialog")

        // 判斷想要切換至哪個 dialog
        const targetDialog = 
            currentDialog.classList.contains("login-dialog")?
            dialogs.signup : dialogs.login

        currentDialog.close()
        targetDialog.showModal()
    })

})

// 預設一開始開啟的會是「登入」
const dialogTrigger = document.querySelector("[data-dialog-trigger]")
dialogTrigger.addEventListener('click',(e)=>{
    e.preventDefault()
    dialogs.login.showModal()
})

// 按 ❌ 關閉 dialog
document.querySelectorAll(".dialog__close-btn").forEach(button=>{
    button.addEventListener("click", (e)=>{
        button.closest(".dialog").close()
    })
})

// ============ API請求 - 資料抓取 ============ 
async function fetchData(url) {
    try{
        const response = await fetch(url, {
            method: "GET"
        })

        // 檢查 HTTP 狀態碼
        if (!response.ok){
            throw new Error(`伺服器錯誤: ${response.status}`)
        }

        // ============ 解析 JSON ============
        const result = await response.json()
        if (!result.data){
            throw new Error("API 返回了無效的格式");
        }
        
        return result
    } catch (error) {
        console.error("API載入失敗", error)
        return null;  // 失敗時回傳 null
    }
}