from datetime import date
from models.booking import BookingData

def booking_date_has_passed(booking_date_str:str) -> bool:
    # date.fromisoformat 可以直接處理 "YYYY-MM-DD"
    return date.fromisoformat(booking_date_str) < date.today()
    # 原版
    # YYYY, MM, DD = booking_date.split("-")
    # date_obj = date(int(YYYY), int(MM), int(DD))


def sync_booking_data(user_id, data:BookingData, cnx):
    cursor = None
    try:
        cursor = cnx.cursor(dictionary=True)

        # 1. 檢查是否有 active 的預約
        cursor.execute("""
            SELECT * FROM booking WHERE user_id=%s AND booking_status='active'
        """, (user_id,))

        exsiting_booking = cursor.fetchone()

        if exsiting_booking:
            # 2. 更新現有預約
            cursor.execute("""
                UPDATE booking 
                SET attraction_id=%s, date=%s, time=%s, price=%s
                WHERE id=%s
            """, (data.attractionId, data.date, data.time, data.price, exsiting_booking['id']))
            
        else:
            # 3. 建立新預約
            cursor.execute("""
                INSERT INTO booking 
                (user_id, attraction_id, date, time, price) VALUES(%s,%s,%s,%s,%s)
            """, (user_id, data.attractionId, data.date, data.time, data.price))

        cnx.commit()
    except Exception as e:
        cnx.rollback()
        raise e
    finally:
        cursor.close()

def search_active_booking(user_id, cnx):
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
        """,(user_id,))

        return cursor.fetchone()
    
    except Exception as e:
        print(f"資料庫錯誤: {str(e)}")
        raise e

    finally:
        if cursor:
            cursor.close()


def cancel_current_booking(user_id, cnx):
    cursor = None
    try:
        cursor = cnx.cursor()
        cursor.execute("""
            UPDATE booking SET booking_status='cancelled' 
            WHERE user_id=%s AND booking_status='active';
        """,(user_id,))

        cnx.commit()
    
    except Exception as e:
        cnx.rollback()
        print(f"資料庫錯誤：{str(e)}")
        raise e

    finally:
        if cursor:
            cursor.close()