import httpx
from datetime import datetime
from models.order import Order, CreateOrderData
from core.config import PARTNER_KEY


def generate_order_number(user_id):
    now = datetime.now()
    time_str = now.strftime("%Y%m%d%H%M%S")

    user_str = str(user_id).zfill(4)

    return f"{time_str}{user_str}"


def create_order_transaction(cnx, user_id, data:CreateOrderData):
    cursor = None
    try:
        cursor = cnx.cursor()
        order_number = generate_order_number(user_id)
        cursor.execute("""INSERT INTO order_record 
                        (number, user_id, price, 
                        attraction_id, attraction_name, attraction_address, attraction_image, 
                        trip_date, trip_time, 
                        contact_name, contact_email, contact_phone)
                        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)""",
                        (order_number, user_id, data.order.price,
                        data.order.trip.attraction.id, data.order.trip.attraction.name, data.order.trip.attraction.address, data.order.trip.attraction.image,
                        data.order.trip.date, data.order.trip.time,
                        data.order.contact.name, data.order.contact.email, data.order.contact.phone))
        cnx.commit() # 先 commit 第一次，避免後面報錯rollback連嘗試的紀錄都不見
        return order_number #成功了就回傳訂單編號
        
    except Exception as e:
        cnx.rollback()
        print(f"Database Error in create_order: {e}")
        raise e
    
    finally:
        if cursor:
            cursor.close()


# https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime
async def fetch_tappay(url, headers, body):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
        print(response.json())  # 輸出 API 回應
        return response.json()


async def fetch_tappay_from_service(data:CreateOrderData):
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
    response = await fetch_tappay(url, headers, body)
    return response


def update_order_detail(cnx, user_id, order_number, db_status, rec_trade_id):
    cursor = None
    try:
        cursor = cnx.cursor()
        if db_status == 1:
            cursor.execute("DELETE FROM booking WHERE user_id=%s AND booking_status='active'",(user_id,))

        # 不論成功或失敗都放入 rec_trade_id 供未來和tappay查詢
        cursor.execute("""UPDATE order_record SET status=%s, tappay_rec_trade_id=%s
                        WHERE number=%s""",(db_status, rec_trade_id, order_number))
        
        cnx.commit()

    except Exception as e:
        cnx.rollback()
        print(f"Database Error in update_order: {e}")
        raise e
    
    finally:
        if cursor:
            cursor.close()


def get_order_record_from_db(orderNumber, cnx):
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM order_record WHERE number=%s", (orderNumber,))

        result = cursor.fetchone()

        return Order.actualizer(result) #透過預先定義好的classmethod組裝格式
    
    except Exception as e:
        print(f"查詢訂單出錯: {e}")
        return None

    finally:
        if cursor:
            cursor.close()