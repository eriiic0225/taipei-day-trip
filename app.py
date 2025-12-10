from contextlib import asynccontextmanager #非同步/lifespan
from fastapi import *
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles # 靜態網頁資料處理 / 各種檔案
from starlette.middleware.sessions import SessionMiddleware # 使用者狀態管理（week 1尚未使用）
from typing import Optional
import json # 解析json回覆
import os
from dotenv import load_dotenv
#from bcrypt import hashpw, gensalt, checkpw # 用來將密碼加密儲存（week 1尚未使用）
#from pydantic import BaseModel, Field, EmailStr # 自動輸入驗證與型別轉換（week 1尚未使用）
#from fastapi.middleware.cors import CORSMiddleware（week 1尚未使用）
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import errors

#------------------- 取得環境變數內的敏感資料 --------------------
load_dotenv()
db_pwd = os.getenv("DB_PASSWORD") # 資料庫密碼
session_key = os.getenv("SECRET_KEY") # session金鑰

# 建立全域連接池
cnxpool = None
@asynccontextmanager #lifespan - 自動於程式啟動/關閉時運行
async def lifespan(app: FastAPI):
    global cnxpool
    try:
        cnxpool = MySQLConnectionPool(
            pool_name="fastapi_pool",          # 連接池名稱（唯一標識）
            pool_size=10,                      # 初始連接池大小（預先建立 10 個連接）
            pool_reset_session=True,           # 每次取得連接時重置會話（清除上一個操作的狀態）
            host="localhost",                  # MySQL 服務器地址
            user="wehelpS2",                       # 資料庫使用者名稱
            password=db_pwd,                   # 資料庫密碼
            database="taipei_attractions"      # 預設資料庫名稱
        )
        print("✓ 連接池已初始化，大小: 10")

    except errors.Error as e:
        print(f"✗ 連接池初始化失敗: {str(e)}")
        raise
    
    yield
    
    # 應用程式關閉時清理
    print("✓ 應用程式關閉，連接池清理完成")

#------------------- 宣告 FastAPI 物件 --------------------
app=FastAPI(lifespan=lifespan)

#---------------------- 連接池相關設置 ----------------------
# 依賴注入函式，為每個請求取得連接
def get_db():
    global cnxpool
    cnx = cnxpool.get_connection() # 從連接池取得一個可用連接
    try:
        yield cnx # 提供連接給路由函式
    finally:
        cnx.close()  # 歸還連接到連接池 # 使用連接的 API 端點

#---------- 使用 SessionMiddleware，密鑰為任意字串 ----------
app.add_middleware(
    SessionMiddleware, 
    secret_key = session_key
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

# ------------ week 1 - API ------------
@app.get("/api/attractions")
async def search_attractions(
	page:int = Query(0,ge=0),
	category: Optional[str] = Query(None), 
	keyword: Optional[str] = Query(None),
	cnx=Depends(get_db)
):
	page_size = 8
	cursor1 = cnx.cursor(dictionary=True) #抓資訊
	cursor2 = cnx.cursor() #抓image_url，以陣列形式回傳response
    
	try:
		offset = page * page_size

		# 動態構造 WHERE 條件
		conditions = []
		params = []
        
		if category:
			conditions.append("category=%s")
			params.append(category)

		if keyword:
			conditions.append("(mrt=%s OR name REGEXP %s)")
			params.extend([keyword, keyword])

		where_clause = " AND ".join(conditions) if conditions else "1=1"

		sql = f"""SELECT * FROM attractions
		WHERE {where_clause}
		LIMIT 8 OFFSET {offset}"""

		cursor1.execute(sql, tuple(params))
		result = cursor1.fetchall()

		# 抓圖片URL並與景點主資訊整合
		for info in result:
			attraction_id = info.get("id")
			cursor2.execute(
				"""SELECT attractions_images.image_url FROM attractions_images 
				WHERE attraction_id=%s""", [attraction_id])
			nest_urls = cursor2.fetchall()
			image_urls  = [url[0] for url in nest_urls]
			info["images"] = image_urls

		# 確認是否有下一頁
		check_next_page = f"""SELECT * FROM attractions
		WHERE {where_clause}
		LIMIT 1 OFFSET {(page+1)* page_size}"""

		cursor1.execute(check_next_page, tuple(params))
		has_next_page = len(cursor1.fetchall()) > 0
		nextPage = (page + 1) if has_next_page else None

		context = {
			"nextPage": nextPage,
			"data": result,	
		}

		return context

		# ("""SELECT * FROM attractions
		# WHERE category=%s AND (mrt=%s OR name REGEXP %s)
		# LIMIT 8 OFFSET %s""",(參數們))

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)
    
	finally:
		cursor1.close()
		cursor2.close()

@app.get("/api/attractions/{attractionsId}")
async def attractions_by_id(attractionsId:int, cnx=Depends(get_db)):
	cursor1 = cnx.cursor(dictionary=True) #抓資訊
	cursor2 = cnx.cursor() #抓url
	try:
		cursor1.execute(
			"""SELECT * FROM attractions WHERE id=%s""", [attractionsId]
		)
		attraction = cursor1.fetchone()
		if not attraction:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "景點編號查無資料"
				}
			)
		
		cursor2.execute(
			"""SELECT attractions_images.image_url FROM attractions_images 
			WHERE attraction_id=%s""", [attractionsId])
		image_urls = [url[0] for url in cursor2.fetchall()]
		attraction["images"] = image_urls

		return {"data": attraction}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)
    
	finally:
		cursor1.close()
		cursor2.close()

@app.get("/api/categories")
async def list_categories(cnx=Depends(get_db)):
	cursor = cnx.cursor()
	try :
		cursor.execute("SELECT category FROM attractions GROUP BY category ORDER BY category DESC")
		result = cursor.fetchall()
		categories = [category[0] for category in result]
		return {"data": categories}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)

	finally:
		cursor.close()

@app.get("/api/mrts")
async def list_mrts(cnx=Depends(get_db)):
	cursor = cnx.cursor()
	try :
		cursor.execute(
			"""SELECT mrt, COUNT(*)AS num 
			FROM attractions 
			WHERE mrt IS NOT NULL AND mrt !=''
			GROUP BY mrt ORDER BY num DESC;""")
			# SQL中判斷 NULL 需要要用 IS NULL 或 IS NOT NULL
		result = cursor.fetchall()
		mrts = [mrt[0] for mrt in result]
		return {"data": mrts}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)

	finally:
		cursor.close()