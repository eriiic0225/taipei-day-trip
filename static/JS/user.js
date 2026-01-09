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

// ==== 顯示錯誤訊息(給登入/註冊使用) ====
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

    const submitBtn = form.querySelector(".dialog__form-btn")
    const originalText = submitBtn.textContent

    try{
        submitBtn.disabled = true
        submitBtn.textContent = "處理中..."

        const formData = new FormData(form)

        const payload = {
            email: formData.get("email").toLowerCase().trim(),
            password: formData.get("password").trim()
        }

        const result = await apiCall("/api/user/auth", "PUT", payload)

        localStorage.setItem("token", result.token)

        showMessage(form, "✅ 登入成功！", false)

        setTimeout(()=>{
            location.reload()
        },1000)

    }catch(error){
        console.error("登入失敗", error)
        showMessage(form, `❌ ${error.message}`, true)
    } finally {
        submitBtn.disabled = false
        submitBtn.textContent = originalText
    }
}

// ==== 註冊 ====
async function signUp(form) {

    const submitBtn = form.querySelector(".dialog__form-btn")
    const originalText = submitBtn.textContent

    try{
        submitBtn.disabled = true
        submitBtn.textContent = "處理中..."

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
    } finally {
        submitBtn.disabled = false
        submitBtn.textContent = originalText
    }
}

// ==== 監聽登入＆註冊的form提交 ====
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

//! ==== 檢查登入狀態 - 頁面載入時自動確認用戶使否登入 ====
async function checkUserStates(){
    const token = localStorage.getItem("token")
    if (!token) return null
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
            return null
        }
        return result.data
    }catch(error){
        console.error("伺服器錯誤：", error)
        return null
    }
}


// ==== 確認所有頁面右上角的登入/登出的顯示狀態 ====
async function RenderLoginStatus(){
    const user = await checkUserStates() 
    if (user){
        //如果登入成功 => 渲染 - 從「登入註冊」改「登出系統」
        const loginStates = document.querySelector(".navbar_login-states")
        loginStates.innerHTML = 
            `<a href="#" class="navbar__link" onclick="logout()">登出系統</a>`
    }
}

// ==== 初始化 ====
async function initUserFeatures() {
    await loadAuthDialog()
    await RenderLoginStatus()
    BookingPageRedirctCheck() // week 5 
}

document.addEventListener("DOMContentLoaded", initUserFeatures);

//! week 5 - booking跳轉邏輯函式包裝
function BookingPageRedirctCheck(){
    document.querySelector("[data-booking]").addEventListener("click",async(e)=>{
        e.preventDefault()
        const user = await checkUserStates()
        if (!user) {
            dialogs.login.showModal()
        }else{
            window.location.assign("/booking")
        }
    })
}