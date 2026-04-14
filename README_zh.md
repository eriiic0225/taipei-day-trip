# Taipei Day Trip 台北一日遊

[English Version (英文版)](README.md)

![Python](https://img.shields.io/badge/Python-3.10+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.120+-009688?logo=fastapi)
![MySQL](https://img.shields.io/badge/MySQL-9.5+-4479A1?logo=mysql)
![JWT](https://img.shields.io/badge/Authentication-JWT-orange)

## 📝 Summary
Taipei Day Trip 台北一日遊是一個旅遊電子商務網站。專案提供景點資料瀏覽、行程規劃、導覽時間預定，並整合第三方金流處理線上結帳與訂單建立。

**🌐 網站連結:** [http://13.237.226.245](http://13.237.226.245)

**測試帳號資訊:**
* 帳號：`admin@test.com`
* 密碼：`admin`

**測試用信用卡資訊 (TapPay):**
* 卡片號碼: `4242 4242 4242 4242`
* 過期時間: (任意未來日期)
* 驗證碼 (CVV): `123`

## 🎥 Demo

**1. 景點探索與無限捲動載入 (Infinite Scroll & Carousel)**
![景點探索展示](public/Demo_1.gif)

**2. 行程預定與金流結帳流程 (Booking & Payment)**
![預定與結帳流程](public/Demo_2.gif)

**3. 會員中心：大頭貼更新與歷史訂單 (Member Center & Order History)**
![會員中心展示](public/Demo_3.gif)

## ✨ Main Features

**Attraction (景點探索)**
* 提供關鍵字與捷運站搜尋功能，供使用者精準備尋找相關景點。
* 使用 Intersection Observer API 實作瀑布流 (Infinite scroll) 動態載入，優化長列表的頁面載入體驗。

**Membership System (會員系統)**
* 實作使用者註冊與登入系統，並於前端使用正規表達式 (Regex) 驗證表單輸入格式。
* 後端採用 JSON Web Tokens (JWT) 進行使用者狀態管理與 API 路由保護。
* 提供會員個人化設定，支援基本資料修改與本地圖片大頭貼上傳功能。

**Booking and Payment (預定與結帳)**
* 行程預約系統，允許使用者選擇特定日期與時段 (上午/下午) 並建立待結帳的預定行程。
* 串接 TapPay 第三方金流 API，處理信用卡驗證與扣款以完成安全的線上交易。
* 提供歷史訂單審閱功能，供使用者在專屬頁面檢視過去的交易紀錄與付款狀態。

## 🛠 Techniques

### Frontend
* **Vanilla JavaScript**
* **Fetch API**
* **HTML5 / CSS3 (RWD)**

### Backend & Infrastructure
* **Python 3 / FastAPI**
* **MySQL (mysql-connector-python)**
* **JWT (JSON Web Token)**
* **bcrypt**
* **AWS EC2**
* **Nginx**

## 🏗 Architecture
![Backend Structure](public/backend-structure.png)

後端架構依據職責分離 (Separation of Concerns) 進行目錄劃分：

```text
├── api/             # 路由層，處理 HTTP Request 與 Response 格式
├── core/            # 核心配置，包含環境變數載入與 JWT 驗證中介邏輯
├── database/        # 資料庫連線池設定與初始化匯入腳本
├── models/          # 透過 Pydantic 定義 API 的輸入與輸出資料結構驗證
├── services/        # 業務邏輯層，處理密碼雜湊、金流 API 請求等特定邏輯
├── static/          # 前端靜態資源 (HTML / CSS / JS / Images)
└── app.py           # FastAPI 應用程式入口點與 Middleware (CORS/Session) 設定
```

## 🗄 Database Schema
![Database Structure](public/DB_structure.png)

資料庫結構依據業務邏輯需求，採用第三正規化 (3NF) 與資料快照 (Data Snapshot) 設計：

* **`user`**：儲存會員基本資訊 (名稱、信箱、雜湊密碼、大頭貼路徑)，信箱欄位設為 `UNIQUE`。
* **`attractions`**：儲存景點主檔資料 (名稱、描述、分類、經緯度等)。
* **`attractions_images`**：透過外鍵關聯 `attractions` 表 (多對一)。將景點的圖片網址獨立儲存，符合第三正規化 (3NF) 以消除重複資料。
* **`booking`**：儲存購物車內的預定行程。透過外鍵關聯 `user_id` 與 `attraction_id`，並記錄行程日期與時間。
* **`order_record`**：儲存結帳後的訂單紀錄。此表採用**資料快照 (Snapshot)** 設計，在訂單成立當下，將 `attraction_name`、`attraction_address` 與圖片等結帳資訊直接複製寫入此表。確保使用者的歷史訂單紀錄不受未來 `attractions` 主檔資料變更或刪除的影響。

## 📖 API Doc
後端採用 RESTful API 設計。透過 FastAPI 自動生成的 OpenAPI 規格，專案啟動後可於 `/docs` 路由（如：[http://13.237.226.245/docs](http://13.237.226.245/docs)）訪問 Swagger UI，檢視完整的 API 規格並進行測試。