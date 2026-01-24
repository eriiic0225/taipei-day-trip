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

    initAvatarEventlistener();
    updateUserEventlistener();
});


// 函式：將使用者資料填入頁面
function populateProfileData(user) {
    const profileName = document.getElementById('profile-form-name');
    const profileEmail = document.getElementById('profile-form-email');
    const profileAvatar = document.getElementById('profile-avatar');
    
    // 使用 Optional Chaining (?.) 或檢查是否存在，避免 JS 因為找不到元素而崩潰
    if (profileName) profileName.value = user.name || "";
    if (profileEmail) profileEmail.value = user.email || "";
    if (profileAvatar) profileAvatar.src = user.avatar || defaultAvatar;

    // 清空密碼欄位 (加個選取器檢查更安全)
    const currentPwd = document.getElementById('profile-form-password-current');
    const newPwd = document.getElementById('profile-form-password-new');
    
    if (currentPwd) currentPwd.value = '';
    if (newPwd) newPwd.value = '';
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
async function initAvatarEventlistener() {
    // ==== 頭像上傳邏輯 ====
    const avatarEditButton = document.querySelector('.avatar-edit-button');
    const avatarFileInput = document.getElementById('avatar-file-input');
    const profileAvatarImg = document.getElementById('profile-avatar'); // 取得頭像圖片元素

    if (avatarEditButton && avatarFileInput && profileAvatarImg) {
        // 1. 點擊「更換頭像」按鈕時，觸發隱藏的檔案選擇 input
        avatarEditButton.addEventListener('click', ()=>{
            avatarFileInput.click();
        });

        // 2. 當檔案被選擇時 (input 內容改變)
        avatarFileInput.addEventListener('change', async(event)=>{
            const file = event.target.files[0]; //取得input中上傳的第一個檔案
            if (file){
                const reader = new FileReader();
                reader.onload = (e) => {
                    // 讀取完成後，將結果賦值給 img
                    profileAvatarImg.src = e.target.result; // 更新頭像圖片的 src
                };
                reader.readAsDataURL(file);
                // 執行檔案上傳
                await uploadAvatar(file);
            };
        });
    }
}

async function uploadAvatar(file) {
    const profileFormMessage = document.getElementById('profile-form-message')
    if (!profileFormMessage) return
    const formData = new FormData()
    formData.append('file', file); // 確保這裡叫 'file'(要跟後端接收欄位名稱一致)

    try {
        const response = await fetch('/api/user/auth/avatar', {
            method: "POST",
            body: formData,
            headers: {'Authorization': `Bearer ${localStorage.getItem('token')}`}
        })

        const result = await response.json()

        if (result.ok){
            profileFormMessage.textContent = '頭像更新成功！';
            profileFormMessage.style.color = 'green';
            
            const navAvatar = document.querySelector('.user-profile-button__avatar'); 
            if (navAvatar) navAvatar.src = result.data.url;
        }else{
            throw new Error(result.message)
        }
    }catch (error){
        profileFormMessage.textContent = `上傳失敗: ${error.message}`;
        profileFormMessage.style.color = 'red';
    }finally{
        profileFormMessage.style.display = 'block';
        setTimeout(() => { profileFormMessage.style.display = 'none'; }, 3000)
    }
}

async function updateUserEventlistener(){
    const profileForm = document.getElementById('profile-form')
    profileForm.addEventListener('submit', async(e)=>{
        e.preventDefault()
        
        const name = document.getElementById('profile-form-name').value.trim();
        const oldPassword = document.getElementById('profile-form-password-current').value;
        const newPassword = document.getElementById('profile-form-password-new').value;

        // 2. 動態建構要送出的資料物件 (只放有填的東西)
        const updateData = {};
        if (name) updateData.name = name

        // 3. 密碼邏輯判斷
        if (newPassword) {
            if (!oldPassword) {
                showUpdateMessage('請輸入目前的密碼以進行修改', 'red');
                return;
            }
            updateData.password = oldPassword; // 這裡的 key 要跟後端 Pydantic 對齊
            updateData.new_password = newPassword;
        }

        try {
            const result = await authApiCall('api/user/auth/update', 'PATCH', updateData)
            if (result.ok){
                showUpdateMessage('資料更新成功！', 'green');
                user = await checkUserStates();
                populateProfileData(user)
            }else{
                showUpdateMessage(result.message || '更新失敗', 'red');
            }
        } catch (error) {
        showUpdateMessage('網路連線異常', 'red');
        }
    })
}

// 一個方便顯示訊息的小工具
function showUpdateMessage(text, color) {
    const profileMessage = document.getElementById('profile-form-message')
    profileMessage.textContent = text;
    profileMessage.style.color = color;
    profileMessage.style.display = 'block';
    setTimeout(() => { profileMessage.style.display = 'none'; }, 3000);
}