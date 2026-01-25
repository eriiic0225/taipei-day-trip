# ------------ week 6 - Booking類的API ------------
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
from mysql.connector import errors
from models.user import TokenPayload
from core.dependencies import verify_token
from models.order import *
from services.order_services import *

router = APIRouter(prefix="/api", tags=["order"])


@router.post("/orders")
async def create_order_and_payment(
    data:CreateOrderData, 
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(status_code=403, content={"error": True,"message": "未登入系統，拒絕存取"})
    
    try:
        order_number = create_order_transaction(cnx, payload.id, data)

        # 第二步：打tappay API
        tappay_repsonse = await fetch_tappay_from_service(data)

        print(tappay_repsonse)

        db_status = 1 if tappay_repsonse.get("status") == 0 else 0
        rec_trade_id = tappay_repsonse.get("rec_trade_id")

        # 第三步：根據回應更新資料庫
        update_order_detail(cnx, payload.id, order_number, db_status, rec_trade_id)

        payment = PaymentStatus(status=db_status, message="付款成功" if db_status==1 else "付款失敗")
        
        # 回傳給前端
        return {
            "data":{
                "number": order_number,
                "payment": payment
            }
        }
    
    except Exception as e:
        print(f"伺服器錯誤:{str(e)}")
        return JSONResponse(status_code=500, content={"error": True, "message": "伺服器錯誤"})
    

@router.get("/order/{orderNumber}")
async def get_order(
    orderNumber:str, 
    cnx=Depends(get_db),
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(status_code=403,content={"error": True,"message": "未登入系統，拒絕存取"})
    
    order_obj = get_order_record_from_db(orderNumber, cnx)

    return {"data": order_obj}