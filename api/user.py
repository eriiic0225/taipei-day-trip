# ------------ week 4 - user類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
from mysql.connector import errors
from models.user import CreateUserData, LoginData
from models.user import TokenPayload, Token, UserResponseData
from core.config import MyCustomError
from services import user_service
from services.user_service import get_hashed_password, verify_password, create_access_token, get_user_by_email
from core.dependencies import verify_token



router = APIRouter(prefix="/api/user", tags=["user"])


# ========== 註冊 =========
@router.post("/")
async def create_user(data:CreateUserData, cnx=Depends(get_db)):
    cursor = None
    name = data.name.strip()
    email = data.email.strip()
    password = data.password.strip()

    hash_password = get_hashed_password(password)

    try:
        
        user_service.create_user_in_db(cnx, name, email, hash_password)

        return {"ok": True}

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
@router.put("/auth")
async def user_login(data:LoginData, cnx=Depends(get_db)):
    email = data.email.strip()
    password = data.password.strip()
    cursor = cnx.cursor(dictionary=True)
    try:
        result = get_user_by_email(cursor, email)

        if not result:
            raise MyCustomError("此email尚未註冊！")

        user_id = result['id']
        user_name = result['name']
        stored_hashed_pwd = result['password']

        is_password_correct = verify_password(password, stored_hashed_pwd)

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
    
    user_data = UserResponseData(id=payload.id, name=payload.name, email=payload.email)

    return {
        "data":user_data
    }
