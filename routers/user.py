# ------------ week 4 - user類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import json
from database.connection import get_db
from pydantic import BaseModel, Field, EmailStr # 自動輸入驗證與型別轉換
from bcrypt import hashpw, gensalt, checkpw # 用來將密碼加密儲存
from mysql.connector import errors
from auth.schemas import TokenPayload, Token, UserResponse, MyCustomError
from auth.service import create_access_token, decode_access_token
from auth.dependencies import verify_token



router = APIRouter(prefix="/api/user", tags=["user"])


# ========== 註冊 =========
class CreateUserData(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    email: EmailStr  # 自動驗證郵箱格式
    password: str

@router.post("/")
async def create_user(data:CreateUserData, cnx=Depends(get_db)):
    cursor = None
    name = data.name.strip()
    email = data.email.strip()
    password = data.password.strip()

    salt = gensalt()
    encode_password = password.encode('utf-8') #字串 → 位元組（bytes）/ 字符串轉成位元組
    hash_password = hashpw(encode_password, salt) #透過hashpw()把兩個位元組(密碼本身和鹽值)透過演算法打散混合

    try:
        cursor = cnx.cursor()
        cursor.execute("""
            INSERT INTO user(name, email, password)
            VALUES(%s, %s, %s)
        """,(name, email, hash_password))
        cnx.commit()

        return JSONResponse(
            status_code=200,
            content={"ok": True}
        )

    except errors.IntegrityError as e:
        cnx.rollback()
        print(f"資料完整性錯誤: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True, 
                "message": "此email已註冊"
            }
        )
    
    except errors.Error as e:
        cnx.rollback()
        print(f"資料庫錯誤: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error":True,
                "message": "資料庫錯誤"
            }
        )
    
    except Exception as e:
        cnx.rollback()
        print(f"伺服器錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message": "伺服器錯誤"
            }
        )
    
    finally:
        if cursor:
            cursor.close()

# ========== 登入 / 回傳 JWT token =========
class LoginData(BaseModel):
    email: EmailStr
    password: str


@router.put("/auth")
async def user_login(data:LoginData, cnx=Depends(get_db)):
    email = data.email.strip()
    password = data.password.strip()
    cursor = cnx.cursor(dictionary=True)
    try:
        cursor.execute("""SELECT * FROM user WHERE email=%s""",(email,))
        result = cursor.fetchone()

        if not result:
            raise MyCustomError("此email尚未註冊！")

        user_id = result['id']
        user_name = result['name']
        stored_hashed_pwd = result['password']

        # 把從資料庫取出的加密密碼轉回 bytes
        # 檢查 stored_hashed_pwd 是否是字符串
        if isinstance(stored_hashed_pwd, str): #如果是 str → 轉換成 bytes
            stored_hashed_pwd = stored_hashed_pwd.encode('utf-8')

        password = password.encode('utf-8') # 把從前端收到的結果轉換後才能比對
        is_password_correct = checkpw(password, stored_hashed_pwd)

        if not is_password_correct:
            raise MyCustomError("密碼不正確")
        
        # 比對成功 => 把 user_id, name, email 組成payload，再生成token
        token = create_access_token(user_id, user_name, email)
        print(token)

        return Token(token=token)
    
    except MyCustomError as e:
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": str(e)
            }
        )
    
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )
    
    finally:
        cursor.close()


# ========== 取得當前登入使用者的資訊 =========
@router.get("/auth")
async def get_current_user(
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return {"data": None}
    
    user_data = UserResponse(id=payload.id, name=payload.name, email=payload.email)

    return {
        "data":user_data
    }