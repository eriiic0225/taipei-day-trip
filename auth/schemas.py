# 數據結構
# 用 Pydantic 定義 JWT payload 和回應格式

from pydantic import BaseModel, EmailStr
from typing import Optional

# JWT Payload 結構（token 裡面放什麼資料）
# 當 JWT token 被解密時，用這個 class 確保解出來的資料格式正確。
class TokenPayload(BaseModel):
    id: int
    name: str
    email: str

# 登入時回傳的 token
# 定義登入 API 的回應格式
class Token(BaseModel):
    token: str # 實際的 JWT token 字串
    # token_type: str = "bearer" #告知前端 token 的類型（預設值 "bearer"）

# 用戶基本資訊（登入成功或取得用戶資訊時回傳）
class UserResponse(BaseModel):
    id: int
    name: str
    email: str  

# 用來捕捉自定義錯誤，以符合任務API文件要求的規格
class MyCustomError(Exception):
    pass