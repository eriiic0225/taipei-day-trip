# 存放 JWT 的所有常數設定

import os
from datetime import timedelta
from dotenv import load_dotenv

load_dotenv()

# JWT 相關設置
JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY") #從環境變數取得金鑰
JWT_ALGORITHM = "HS256" # 加密方式
ACCESS_TOKEN_EXPIRE_DAYS = 7  # token 7天後過期
# 轉換成 timedelta（service.py 會需要用到）
# ACCESS_TOKEN_EXPIRE_TIME = timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)

if not JWT_SECRET_KEY:
    raise ValueError(
        "錯誤： .env 未設定 JWT_SECRET_KEY"
    )

# 取的 Tappay Partner Key
PARTNER_KEY = os.getenv("PARTNER_KEY")

if not PARTNER_KEY:
    raise ValueError(
        "錯誤： .env 未設定 PARTNER_KEY"
    )


# 用來捕捉自定義錯誤，以符合任務API文件要求的規格
class MyCustomError(Exception):
    pass