# ------------ week 5 - booking類的API ------------
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
import mysql.connector
from models.user import TokenPayload
from models.booking import BookingData, Booking, BookingAttraction
from core.dependencies import verify_token
from datetime import date

router = APIRouter(prefix="/api", tags=["booking"])

@router.post("/booking")
async def create_booking(
    data:BookingData, 
    payload:Optional[TokenPayload]= Depends(verify_token) ,
    cnx=Depends(get_db)):

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )

    booked_date = data.date
    YYYY, MM, DD = booked_date.split("-")
    date_obj = date(int(YYYY), int(MM), int(DD))

    if date_obj < date.today():
        return JSONResponse(
            status_code=400,
            content={"error": True, "message": "不可預定已過日期！"}
        )
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)
        user_id = payload.id
        attraction_id = data.attractionId
        time_slot = data.time
        price = data.price

        cursor.execute("""
            SELECT * FROM booking WHERE user_id=%s AND booking_status='active'
        """, (user_id,))

        result = cursor.fetchone()

        if result is None:
            cursor.execute("""
                INSERT INTO booking 
                (user_id, attraction_id, date, time, price) VALUES(%s,%s,%s,%s,%s)
        """, (user_id, attraction_id, booked_date, time_slot, price))

        else:
            cursor.execute("""
                UPDATE booking 
                SET attraction_id=%s, date=%s, time=%s, price=%s
                WHERE user_id=%s AND booking_status='active'
        """, (attraction_id, booked_date, time_slot, price, user_id))
        
        cnx.commit()
        return {"ok": True}


    except mysql.connector.Error as err:
        cnx.rollback()
        print(f"❌ 執行失敗: {str(err)}")
        return JSONResponse(
            status_code=400,
            content={
                "error": True,
                "message": "建立失敗，輸入不正確或其他原因"
            }
        )
    
    except Exception as e:
        cnx.rollback()
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={
                "error": True,
                "message": "伺服器內部錯誤"
            }
        )
    
    finally:
        if cursor:
            cursor.close()

@router.get("/booking")
async def get_current_booking(
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):
    
    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )
    
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("""
            SELECT 
                a.id, 
                a.name, 
                a.address ,
                (SELECT image_url FROM attractions_images 
                    WHERE attraction_id=a.id LIMIT 1) AS image, 
                b.date, 
                b.time, 
                b.price 
            FROM attractions a INNER JOIN booking b ON a.id=b.attraction_id
            WHERE b.user_id=%s AND b.booking_status='active';
        """,(payload.id,))
        result = cursor.fetchone()

        if result is None:
            return {"data": None}
        
        attraction = BookingAttraction(
            id = result["id"],
            name = result["name"],
            address = result["address"],
            image = result["image"]
        )

        booking = Booking(
            attraction = attraction,
            date = str(result["date"]), # date從 MySQL拿出來會是 date 物件，需要特別處理
            time = result["time"],
            price = result["price"]
        )

        return { "data": booking }
    
    except Exception as e:
        print(f"❌ 執行失敗: {str(e)}")
        return {"data": None}
    
    finally:
        if cursor:
            cursor.close()

@router.delete("/booking")
async def cancel_booking(
    cnx=Depends(get_db), 
    payload:Optional[TokenPayload]=Depends(verify_token)):

    if payload is None:
        return JSONResponse(
            status_code=403,
            content={"error": True, "message": "未登入系統，拒絕存取"}
        )
    
    cursor = None
    try:
        cursor = cnx.cursor()
        cursor.execute("""
            UPDATE booking SET booking_status='cancelled' 
            WHERE user_id=%s AND booking_status='active';
        """,(payload.id,))

        cnx.commit()
        return {"ok": True}
    
    except Exception as e:
        cnx.rollback()
        print(f"❌ 執行失敗: {str(e)}")
        return JSONResponse(
            status_code=500,
            content={"error": True, "message": "伺服器錯誤"}
        )
    
    finally:
        if cursor:
            cursor.close()