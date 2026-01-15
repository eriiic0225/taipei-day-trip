# ------------ week 4 - user類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
from mysql.connector import errors
from models.user import CreateUserData, LoginData
from models.user import TokenPayload, Token, UserResponse
from core.config import MyCustomError
from services import user_service
from services.user_service import get_hashed_password, verify_password, create_access_token, get_user_by_email
from core.dependencies import verify_token
from models.order import *
from core.config import PARTNER_KEY
from services.order_services import *

router = APIRouter(prefix="/api", tags=["order"])



@router.post("/orders")
async def create_order_and_payment(
    data:CreateOrderData, 
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True,"message": "未登入系統，拒絕存取"}
        )
    
    cursor = None
    try:
        order_number = generate_order_number(payload.id)
        # 第一步：在資料庫寫入 unpaid 的紀錄
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""INSERT INTO order_record 
                        (number, user_id, price, 
                        attraction_id, attraction_name, attraction_address, attraction_image, 
                        trip_date, trip_time, 
                        contact_name, contact_email, contact_phone)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (order_number, payload.id, data.order.price,
                        data.order.trip.attraction.id, data.order.trip.attraction.name, data.order.trip.attraction.address, data.order.trip.attraction.image,
                        data.order.trip.date, data.order.trip.time,
                        data.order.contact.name, data.order.contact.email, data.order.contact.phone))
        cnx.commit() # 先 commit 第一次，避免後面報錯rollback連嘗試的紀錄都不見

        # 第二步：打tappay API
        url = "https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime"
        body={
            "prime": data.prime,
            "partner_key": PARTNER_KEY,
            "merchant_id": "eriiic0225_CTBC",
            "details":"TapPay Test",
            "amount": data.order.price,
            "cardholder": {
                "phone_number": data.order.contact.phone,
                "name": data.order.contact.name,
                "email": data.order.contact.email,
            }
        }
        headers={"x-api-key": PARTNER_KEY} # httpx 使用 json= 會自動帶 content-type

        tappay_repsonse = await fetch_tappay(url, headers, body)
        print(tappay_repsonse)

        db_status = 0
        rec_trade_id = None

        # 第三步：根據回應更新資料庫
        if tappay_repsonse.get("status") == 0:
            db_status = 1
            rec_trade_id = tappay_repsonse.get("rec_trade_id")
            # 成功時才刪除預約(booking)
            cursor.execute("DELETE FROM booking WHERE user_id=%s AND booking_status='active'",(payload.id,))
        
        # 不論成功或失敗都放入 rec_trade_id 供未來和tappay查詢
        cursor.execute("""UPDATE order_record SET status=%s, tappay_rec_trade_id=%s
                        WHERE number=%s""",(db_status, rec_trade_id, order_number))
        
        cnx.commit()

        payment = PaymentStatus(status=db_status, message="付款成功" if db_status==1 else "付款失敗")
        
        # 回傳給前端
        return {
            "data":{
                "number": order_number,
                "payment": payment
            }
        }
    
    except Exception as e:
        cnx.rollback()
        print(f"伺服器錯誤:{str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器錯誤"}
        )
    

@router.get("/order/{orderNumber}")
async def get_order(
    orderNumber:str, 
    cnx=Depends(get_db),
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True,"message": "未登入系統，拒絕存取"}
        )
    
    result = get_order_record_from_db(orderNumber, cnx)

    return result