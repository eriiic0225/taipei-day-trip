# 跟連線資料庫相關的設定放在這邊

from contextlib import asynccontextmanager #非同步/lifespan
from dotenv import load_dotenv
from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import errors
import os

#------------------- 取得環境變數內的敏感資料 --------------------
load_dotenv()
db_pwd = os.getenv("DB_PASSWORD") # 資料庫密碼

# 建立全域連接池
cnxpool = None
@asynccontextmanager #lifespan - 自動於程式啟動/關閉時運行
async def lifespan(app):
    global cnxpool
    try:
        cnxpool = MySQLConnectionPool(
            pool_name="fastapi_pool",          # 連接池名稱（唯一標識）
            pool_size=10,                      # 初始連接池大小（預先建立 10 個連接）
            pool_reset_session=True,           # 每次取得連接時重置會話（清除上一個操作的狀態）
            host="localhost",                  # MySQL 服務器地址
            user="wehelpS2",                   # 資料庫使用者名稱
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

#---------------------- 連接池相關設置 ----------------------
# 依賴注入函式，為每個請求取得連接
def get_db():
    global cnxpool
    cnx = cnxpool.get_connection() # 從連接池取得一個可用連接
    try:
        yield cnx # 提供連接給路由函式
    finally:
        cnx.close()  # 歸還連接到連接池 # 使用連接的 API 端點