# 數據結構
# 用 Pydantic 定義 JWT payload 和回應格式

from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class CreateUserData(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr  # 自動驗證郵箱格式
    password: str

class LoginData(BaseModel):
    email: EmailStr
    password: str

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
class UserResponseData(BaseModel):
    id: int
    name: str
    email: str  

class UserResponse(BaseModel):
    data: Optional[UserResponseData] = None