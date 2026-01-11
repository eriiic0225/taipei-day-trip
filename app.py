from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles # 靜態網頁資料處理 / 各種檔案
from starlette.middleware.sessions import SessionMiddleware # 使用者狀態管理（week 1尚未使用）
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv

# 引入搬移出去的代碼
from database.connection import lifespan
from api import attractions, user
from api import booking as booking_api # 改名引入，避開下方的 def booking(不然會報錯)
#------------------- 取得環境變數內的敏感資料 --------------------
load_dotenv()
session_key = os.getenv("SECRET_KEY") # session金鑰


#------------------- 宣告 FastAPI 物件 --------------------
app=FastAPI(lifespan=lifespan)


#---------- 使用 SessionMiddleware，密鑰為任意字串 ----------
app.add_middleware(
    SessionMiddleware, 
    secret_key = session_key
)

#---------- 允許跨來源請求 CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500",      # ← Live Server 的 port
        "http://localhost:3000",      # 如果你用 React 開發
    ],
    allow_credentials=True, # 允許發送 Cookie 和認證信息（Session）
    allow_methods=["*"],  # 允許所有 HTTP 方法
    allow_headers=["*"],  # 允許所有標頭
)

# Static Pages (Never Modify Code in this Block)
@app.get("/", include_in_schema=False)
async def index(request: Request):
	return FileResponse("./static/index.html", media_type="text/html")
@app.get("/attraction/{id}", include_in_schema=False)
async def attraction(request: Request, id: int):
	return FileResponse("./static/attraction.html", media_type="text/html")
@app.get("/booking", include_in_schema=False)
async def booking(request: Request):
	return FileResponse("./static/booking.html", media_type="text/html")
@app.get("/thankyou", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/thankyou.html", media_type="text/html")


# 包含路由器
app.include_router(attractions.router)
app.include_router(user.router)
app.include_router(booking_api.router)

# ------------------- 統一處理靜態網頁 --------------------
# 物件名稱.mount("網頁前綴", StaticFiles(directory="資料夾名稱"),name="內部名稱")
app.mount("/static", StaticFiles(directory="static"), name="static")