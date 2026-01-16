# 生成和驗證 token
# 核心邏輯 - 編碼和解碼 JWT
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from core.config import JWT_SECRET_KEY, JWT_ALGORITHM, ACCESS_TOKEN_EXPIRE_DAYS
from models.user import TokenPayload
from bcrypt import hashpw, gensalt, checkpw


def get_hashed_password(password: str) -> bytes:
    salt = gensalt()
    encode_password = password.encode('utf-8') #字串 → 位元組（bytes）/ 字符串轉成位元組
    return hashpw(encode_password, salt) 
    #透過hashpw()把兩個位元組(密碼本身和鹽值)透過演算法打散混合


def verify_password(plain_password: str, hashed_password)-> bool:
    # 檢查 hashed_password 是否是字符串
    if isinstance(hashed_password, str): #如果是 str → 轉換成 bytes
        hashed_password = hashed_password.encode('utf-8')
    
    plain_password = plain_password.encode('utf-8')

    return checkpw(plain_password, hashed_password)


# 生成 token
def create_access_token(
        id: int, 
        name: str, 
        email: str, 
        expires_delta: Optional[timedelta] = None
    ) -> str:
#expires_delta 可以是 datetime 模組中的 timedelta 物件，也可以是 None
    """
    生成 JWT token
    """
    # 如果傳入自訂過期時間
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    # 沒有的話就用預設值(7天)
    else:
        expire = datetime.now(timezone.utc) + timedelta(days=ACCESS_TOKEN_EXPIRE_DAYS)
        # 過期時間 = 現在時間 + 7天的差異 aka 從現在算起7天後

    #把使用者資料組合成payload
    payload = {
        "id": id,
        "name": name,
        "email": email,
        "exp": expire
    }
    
    encoded_jwt = jwt.encode(
        payload, # 要編碼的資料
        JWT_SECRET_KEY, # 密鑰（從 config.py）
        algorithm=JWT_ALGORITHM # 演算法（HS256）
    )
    return encoded_jwt # 回傳編碼後的字串


# 驗證和解碼 token，成功後回傳 JWT payload內的內容，並透過pydantic驗證生成物件
# 如果驗證失敗返回 None
def decode_access_token(token: str) -> Optional[TokenPayload]: 
    """
    驗證和解碼 JWT token，如果驗證失敗返回 None
    """
    try:
        payload = jwt.decode(
            token, # 要解密的 token
            JWT_SECRET_KEY, # 用同樣的密鑰
            algorithms=[JWT_ALGORITHM] # 檢查是否用同樣的演算法
        )
        # ✅ JWT 庫會自動檢查 "exp" 是否過期
        id = payload.get("id")
        name = payload.get("name")
        email = payload.get("email")
        
        if id is None or name is None or email is None:
            return None
        
        return TokenPayload(id=id,name=name, email=email)
        # ✅ 驗證成功，回傳 TokenPayload 物件
    except jwt.ExpiredSignatureError:
        print("Token 已過期")
        return None
    except jwt.InvalidTokenError:
        print("Token 無效")
        return None


def get_user_by_email(cursor, email:str):
    """根據 Email 從資料庫取得使用者資料"""
    cursor.execute("SELECT * FROM user WHERE email=%s",(email,))
    return cursor.fetchone()


def create_user_in_db(cnx, name, email, hashed_password):
    """執行註冊 SQL"""
    cursor = cnx.cursor()
    cursor.execute("""
        INSERT INTO user(name, email, password)
        VALUES(%s, %s, %s)
    """,(name, email, hashed_password))
    cnx.commit()
    cursor.close()