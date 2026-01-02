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

// ==== 登出 ====
function logout(){
    localStorage.removeItem("token")
    location.reload()
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
        location.reload()

    }catch(error){
        console.error("登入失敗", error)
        //! 這邊之後要改渲染
        alert(`❌ ${error.message}`)
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

        //TODO 這邊要加成功的dialog訊息渲染，暫時用alert替代
        alert("✅ 註冊成功!")
        form.reset()

    }catch(error){
        console.error("註冊失敗：", error)
        //TODO 這邊要加失敗的dialog訊息渲染，暫時用alert替代
        alert(`❌ ${error.message}`)
    }
}

// ==== 監聽form提交 ====
document.querySelectorAll(".dialog__form").forEach(form=>{
    form.addEventListener("submit", async(e)=>{
        e.preventDefault()
        const formType = form.dataset.form

        if (formType === "login"){
            await login(form)
        } else if (formType === "signup"){
            await signUp(form)
        }
    })
})

// ==== 初始化 ====
checkUserStates()