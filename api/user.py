# ------------ week 4 - user類的API ------------
from fastapi import APIRouter, UploadFile, File, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
from mysql.connector import errors
from models.user import CreateUserData, LoginData
from models.user import TokenPayload, Token, UserResponseData, UserUpdateInput
from core.config import MyCustomError
from services import user_service
from services.user_service import get_hashed_password, verify_password, create_access_token, get_user_by_email, update_db_user_avatar, update_user_fields
from core.dependencies import verify_token

import os
import shutil
import time

UPLOAD_DIR = "static/uploads"

router = APIRouter(prefix="/api/user", tags=["user"])


# ========== 註冊 =========
@router.post("/")
async def create_user(data:CreateUserData, cnx=Depends(get_db)):
    name = data.name.strip()
    email = data.email.strip()
    password = data.password.strip()

    hash_password = get_hashed_password(password)

    try:
        
        user_service.create_user_in_db(cnx, name, email, hash_password)

        return {"ok": True}

    except errors.IntegrityError as e:
        print(f"資料完整性錯誤: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True, 
                "message": "此email已註冊"
            }
        )
    
    except errors.Error as e:
        print(f"資料庫錯誤: {e}")
        return JSONResponse(
            status_code=400,
            content={
                "error":True,
                "message": "資料庫錯誤"
            }
        )
    
    except Exception as e:
        print(f"伺服器錯誤: {e}")
        return JSONResponse(
            status_code=500,
            content={
                "error":True,
                "message": "伺服器錯誤"
            }
        )


# ========== 登入 / 回傳 JWT token =========
@router.put("/auth")
async def user_login(data:LoginData, cnx=Depends(get_db)):
    email = data.email.strip()
    password = data.password.strip()
    try:
        result = get_user_by_email(cnx, email)

        if not result:
            raise MyCustomError("此email尚未註冊！")

        user_id = result['id']
        user_name = result['name']
        stored_hashed_pwd = result['password']

        is_password_correct = verify_password(password, stored_hashed_pwd)

        if not is_password_correct:
            return JSONResponse(
                status_code=400,
                content={
                    "error": True,
                    "message": "密碼不正確"
                }
            )
        
        # 比對成功 => 把 user_id, name, email 組成payload，再生成token
        token = create_access_token(user_id, user_name, email)
        print(token)

        return Token(token=token)
    
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )


# ========== 取得當前登入使用者的資訊 =========
@router.get("/auth")
async def get_current_user(
    payload:Optional[TokenPayload]=Depends(verify_token),
    cnx=Depends(get_db)):

    if payload is None:
        return {"data": None}
    
    result = get_user_by_email(cnx, payload.email)

    if not result: #避免當 result 是 None 時，model_validate 噴出程式錯誤（Exception）
        return {"data": None, "message": "找不到該使用者資料"}
    
    user_data = UserResponseData.model_validate(result)

    return {
        "data":user_data
    }


# ========== 讓使用者可以上傳大頭貼 =========
# 因為對File操作還不熟悉，暫時不對這個 API 做進一步拆解
@router.post("/auth/avatar")
async def api_upload_avatar(
    file: UploadFile = File(...),
    payload: TokenPayload=Depends(verify_token),
    cnx=Depends(get_db)
):
    # 1. 檢查檔案格式 (Input Validation)
    allowed_extensions = ["jpg", "jpeg", "png"]
    file_ext = file.filename.split(".")[-1].lower()
    if file_ext not in allowed_extensions:
        return {"error": True, "message": "不支援的檔案格式"}

    # 2. 自動命名
    # 避免檔名重複，且能透過檔名知道是誰傳的
    user_id = payload.id
    timestamp = int(time.time())
    new_filename = f"user_{user_id}_{timestamp}.{file_ext}"
    file_path = os.path.join(UPLOAD_DIR, new_filename) # 利用os模組拼裝出最終的檔案路徑

    # 3. 寫入硬碟 (硬體寫入)
    # file.file 是一個暫存的二進位流
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 4. 把 file_path 寫入資料庫的該位使用者欄位
    update_db_user_avatar(cnx, user_id, file_path)

    return {
        "ok": True, 
        "data": {"url": f"/{file_path}"} # 回傳路徑給前端預覽
    }


@router.patch("/auth/update")
async def api_update_user_info(data:UserUpdateInput, payload:TokenPayload=Depends(verify_token), cnx=Depends(get_db)):
    update_data = {}

    if data.name:
        update_data["name"] = data.name

    if data.new_password:
        if not data.password: #如果沒有輸入舊的密碼
            return {"error": True, "message": "修改密碼需輸入舊密碼"}
        
        current_user = get_user_by_email(cnx, payload.email)

        # 比對舊密碼
        is_valid = verify_password(data.password, current_user["password"])

        if not is_valid:
            return {"error": True, "message": "舊密碼輸入錯誤"}
        
        # 雜湊新密碼並轉成字串存入字典
        hashed = get_hashed_password(data.new_password)
        update_data["password"] = hashed

    if not update_data:
        return {"error": True, "message": "無更新內容"}
    
    success = update_user_fields(cnx, payload.email, update_data)

    return {"ok": True} if success else {"error": True, "message": "更新失敗"}