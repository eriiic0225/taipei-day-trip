import httpx
from datetime import datetime
from models.order import Order, Trip, Contact
from models.booking import BookingAttraction as Attraction
def generate_order_number(user_id):
    now = datetime.now()
    time_str = now.strftime("%Y%m%d%H%M%S")

    user_str = str(user_id).zfill(4)

    return f"{time_str}{user_str}"

# https://sandbox.tappaysdk.com/tpc/payment/pay-by-prime
async def fetch_tappay(url, headers, body):
    async with httpx.AsyncClient() as client:
        response = await client.post(url, headers=headers, json=body)
        print(response.json())  # 輸出 API 回應
        return response.json()


def get_order_record_from_db(orderNumber, cnx):
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute("SELECT * FROM order_record WHERE number=%s", (orderNumber,))

        result = cursor.fetchone()

        if not result:
            return {"data": None}

        contact = Contact(name=result.get("contact_name"), email=result.get("contact_email"), phone=result.get("contact_phone"))
        attraction = Attraction(id=result.get("attraction_id"), name=result.get("attraction_name"), address=result.get("attraction_address"), image=result.get("attraction_image"))
        trip = Trip(attraction=attraction, date=str(result.get("trip_date")), time=result.get("trip_time"))
        order_data = Order(number=result.get("number"), price=result.get("price"), trip=trip, contact=contact, status=result.get("status"))

        return {"data": order_data}
    
    except Exception as e:
        print(f"查詢訂單出錯: {e}")
        return {"data": None}

    finally:
        if cursor:
            cursor.close()