document.addEventListener('DOMContentLoaded', async () => {
    // 1. 保護頁面：檢查登入狀態，若未登入則導向首頁
    const user = await checkUserStates();
    if (!user) {
        window.location.href = '/';
        return; // 中斷後續程式碼執行
    }

    // 2. 填充使用者資料
    populateProfileData(user);

    // 3. 預留載入歷史訂單的功能
    fetchAndDisplayOrders();
});


// 函式：將使用者資料填入頁面
function populateProfileData(user) {
    const profileName = document.getElementById('profile-name');
    const profileEmail = document.getElementById('profile-email');
    const profileAvatar = document.getElementById('profile-avatar');

    if (profileName) profileName.textContent = user.name;
    if (profileEmail) profileEmail.textContent = user.email;
    
    // 如果 user.avatar 為空，則使用 utils.js 中定義的 defaultAvatar 變數
    if (profileAvatar) profileAvatar.src = user.avatar || defaultAvatar;
}


// 函式：取得並顯示歷史訂單
async function fetchAndDisplayOrders() {
    const orderListContainer = document.getElementById('order-history-list');
    if (!orderListContainer) return;

    // TODO: 未來將在這裡呼叫 API (例如 authApiCallGet('/api/orders')) 來取得真實訂單資料
    
    // 目前，我們先顯示一個預設訊息
    orderListContainer.innerHTML = '<p>目前沒有歷史訂單紀錄。</p>';
    
    // 未來取得資料後的渲染邏輯會寫在這裡...
}

// TODO: 為「編輯資料」和「更換頭像」的按鈕加上事件監聽器，以觸發對應的表單或彈出視窗
