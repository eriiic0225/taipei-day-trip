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