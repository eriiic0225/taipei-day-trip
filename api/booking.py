# ------------ week 5 - booking類的API ------------
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
import mysql.connector
from models.user import TokenPayload
from models.booking import BookingData, Booking
from core.dependencies import verify_token
from services.booking_service import *
import traceback

router = APIRouter(prefix="/api", tags=["booking"])

@router.post("/booking")
async def api_create_booking(
    data:BookingData, 
    payload:Optional[TokenPayload]= Depends(verify_token) ,
    cnx=Depends(get_db)):

    # 權限檢查
    if payload is None:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
    
    # 執行資料庫操作
    try:
        sync_booking_data(payload.id, data, cnx)
        return {"ok": True}

    except mysql.connector.Error as err:
        print(f"❌ 執行失敗: {str(err)}")
        return JSONResponse(status_code=400, content={"error": True, "message": "建立失敗，輸入不正確或其他原因"})
    
    except Exception as e:
        print(f"Server Error: {str(e)}")
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器內部錯誤"})


@router.get("/booking")
async def api_get_current_booking(
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):
    
    if payload is None:
        return JSONResponse(status_code=403,content={"error": True, "message": "未登入系統，拒絕存取"})
    
    try:
        result = search_active_booking(payload.id, cnx)

        if result is None:
            return {"data": None}
        
        # 使用【類別方法】進行封裝與映射
        booking_obj = Booking.create_from_db(result)

        # 直接回傳 obj。FastAPI 會自動把 booking_obj 轉成 JSON
        return {"data": booking_obj}
    
    except Exception as e:
        # 這會印出詳細的報錯位置（在哪個檔案、哪一行）
        traceback.print_exc()
        return {"data": None}


@router.delete("/booking")
async def api_cancel_booking(
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(status_code=403, content={"error": True, "message": "未登入系統，拒絕存取"})
    
    try:
        cancel_current_booking(payload.id, cnx)
        return {"ok": True}
    
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器錯誤"})