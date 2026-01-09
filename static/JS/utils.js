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

// ==== 需要驗證身份的 API call (with body) ====
async function authApiCall(url, method, payload){
    const token = localStorage.getItem("token")
    if (!token) return null
    const response = await fetch(url,{
        method,
        headers:{
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
        body: JSON.stringify(payload)
    })

    const result = response.json()
    if (result.error){
        throw new Error(result.message)
    }

    return result
}

// ==== 需要驗證身份的 API call (GET or Delete/不能有body) ====
async function authApiCallGet(url, method){
    const token = localStorage.getItem("token")
    if (!token) return null
    const response = await fetch(url,{
        method,
        headers:{
            "Content-Type": "application/json",
            "Authorization": "Bearer " + token
        },
    })

    const result = response.json()
    if (result.error){
        throw new Error(result.message)
    }

    return result
}

// === 送出booking請求的函式 ===
async function sendBookingRequest(){
    const bookingInfo = new FormData(bookingForm)
    const bookingDate = bookingInfo.get("book-date")
    const bookingTime = bookingInfo.get("book-time")
    const bookingPrice = bookingForm.querySelector('input[name="book-time"]:checked').dataset.price
    const bookingAttractionId = document.querySelector(".attraction-page__name").dataset.id
    const payload = {
        attractionId: bookingAttractionId,
        date: bookingDate,
        time: bookingTime,
        price: bookingPrice
    }
    const result = await authApiCall("/api/booking", "POST", payload)
    if (result.error){
        throw new Error(result.message)
    }
    return true
}

// ======== 關於圖片預先加載 ========
// 多圖片加載
function imagesPreload(urls){
    return Promise.all(
        urls.map(url => new Promise((resolve, reject)=>{
            const img = new Image
            img.onload = () => resolve({ url, status: 'loaded' });
            img.onerror = () => reject({ url, status: 'failed' });
            img.src = url
        }))
    )
}

// 單圖片預加載
function ImgPreload(url){
    return new Promise((resolve, reject)=>{
        const img = new Image
        img.onload = () => resolve({ url, status: 'loaded' });
        img.onerror = () => reject({ url, status: 'failed' });
        img.src = url
    })
}