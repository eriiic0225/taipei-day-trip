let dialogs

// ============ 動態插入共用的 dialog ============
async function loadAuthDialog() {
    try{
        const response = await fetch("/static/components/auth-dialog.html")
        const html = await response.text()
        document.body.insertAdjacentHTML("beforeend", html)
        // console.log("✅ Auth dialog 載入成功")

        dialogs = {
            login: document.querySelector(".login-dialog"),
            signup: document.querySelector(".signup-dialog")
        }

    }catch(e){
        console.error("❌ Auth dialog 載入失敗:", error)
    }
}

// ============ Pop Up Dialog 開關監聽 ============
document.addEventListener("click", (e)=>{
    // 打開 Dialog(預設Login)
    if (e.target.matches("[data-dialog-trigger]")){
        e.preventDefault()
        dialogs.login.showModal()
    }

    // 登入/註冊切換
    if (e.target.matches(".dialog__switch")){
        e.preventDefault()

        const currentDialog = e.target.closest(".dialog")
        const targetDialog = 
            currentDialog.classList.contains("login-dialog")?
            dialogs.signup : dialogs.login

        currentDialog.close()
        targetDialog.showModal()
    }

    // 按 ❌ 關閉 dialog
    if (e.target.closest(".dialog__close-btn")){
        e.target.closest(".dialog").close()
    }
})


// ==== 共用 - API 函式 ====
async function apiCall(url, method, payload){
    const response = await fetch(url,{
        method,
        headers:{"Content-Type": "application/json"},
        body: JSON.stringify(payload)
    })

    const result = await response.json()

    if (result.error){
        throw new Error(result.message)
    }

    return result
}


// ==== 檢查登入狀態 - 頁面載入時自動確認用戶使否登入 ====
async function checkUserStates(){
    const token = localStorage.getItem("token")
    if (!token) return
    try{
        let response = await fetch("/api/user/auth",{
            method:"GET",
            headers:{
                "Authorization": "Bearer " + token
            }
        })
        if (!response.ok){
            throw new Error(`伺服器錯誤: ${response.status}`)
        }
        let result
        try {
            result = await response.json()
        } catch (e) {
            throw new Error("伺服器返回了無效的 JSON")
        }
        if (!result.data){
            //移除無效的 token
            localStorage.removeItem("token")
        }
        //渲染 - 從「登入註冊」改「登出系統」
        const loginStates = document.querySelector(".navbar_login-states")
        loginStates.innerHTML = 
            `<a href="#" class="navbar__link" onclick=logout()>登出系統</a>`
    }catch(error){
        console.error("伺服器錯誤：", error)
    }
}

// ==== 顯示錯誤訊息 ====
function showMessage(form, message, isError = false){
    const messageEl = form.querySelector(".dialog__message")

    messageEl.textContent = message

    isError?messageEl.style.color = "tomato":messageEl.style.color = "cornflowerblue"

    messageEl.style.display = "block"

    setTimeout(()=>{
        messageEl.style.display = "none"
    },5000)
}

// ==== 登入 ====
async function login(form) {
    try{
        const formData = new FormData(form)

        const payload = {
            email: formData.get("email").toLowerCase().trim(),
            password: formData.get("password").trim()
        }

        const result = await apiCall("/api/user/auth", "PUT", payload)

        console.log(result)
        localStorage.setItem("token", result.token)

        showMessage(form, "✅ 登入成功！", false)

        setTimeout(()=>{
            location.reload()
        },1000)

    }catch(error){
        console.error("登入失敗", error)
        showMessage(form, `❌ ${error.message}`, true)
    }
}

// ==== 註冊 ====
async function signUp(form) {
    try{
        const formData = new FormData(form)

        const payload = {
            name: formData.get("name").trim(),
            email: formData.get("email").toLowerCase().trim(),
            password: formData.get("password").trim()
        }

        // 如果註冊失敗會由子函式拋出錯誤
        const result = await apiCall("/api/user", "POST", payload)

        showMessage(form, "✅ 註冊成功!，請登入", false)
        form.reset()

        setTimeout(()=>{
            form.closest(".dialog").close()
            dialogs.login.showModal()
        },2000)

    }catch(error){
        console.error("註冊失敗：", error)
        showMessage(form, `❌ ${error.message}`, true)
    }
}

// ==== 監聽form提交 ====
document.addEventListener("submit", async(e)=>{
    if (e.target.matches(".dialog__form")){
        e.preventDefault()
        let form = e.target
        const formType = form.dataset.form

        if (formType === "login"){
            await login(form)
        } else if (formType === "signup"){
            await signUp(form)
        }
    }
})


// ==== 登出 ====
function logout(){
    localStorage.removeItem("token")
    location.reload()
}


// ==== 初始化 ====
async function initUserFeatures() {
    await loadAuthDialog()
    checkUserStates()
}

document.addEventListener("DOMContentLoaded", initUserFeatures);