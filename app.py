from fastapi import *
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles # 靜態網頁資料處理 / 各種檔案
from starlette.middleware.sessions import SessionMiddleware # 使用者狀態管理（week 1尚未使用）
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from database.connection import lifespan
from api import attractions, user, order
from api import booking as booking_api # 改名引入，避開下方的 def booking(不然會報錯)
# Pydantic 自動報錯驗證的攔截器
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

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

#---------- 攔截 Pydantic 驗證錯誤 ----------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # exc.errors() 包含了所有出錯的欄位和原因
	# exc.errors() 是一個 list，抓出第一個錯誤的訊息 (msg)
	errors = exc.errors()
	error_msg = errors[0].get("msg") if errors else "輸入格式不正確"
	
	print(f"參數驗證失敗: {errors}")

	return JSONResponse(
        status_code=400, # 把原本的 422 統一改成 400
        content={
            "error": True,
            "message": f"無效的輸入：{error_msg}"
        },
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
# 新增：會員頁面
@app.get("/member", include_in_schema=False)
async def thankyou(request: Request):
	return FileResponse("./static/member.html", media_type="text/html")


# 包含路由器
app.include_router(attractions.router)
app.include_router(user.router)
app.include_router(booking_api.router)
app.include_router(order.router)

# ------------------- 統一處理靜態網頁 --------------------
# 物件名稱.mount("網頁前綴", StaticFiles(directory="資料夾名稱"),name="內部名稱")
app.mount("/static", StaticFiles(directory="static"), name="static")