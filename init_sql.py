import json
import re
import os
from dotenv import load_dotenv
import mysql.connector # 連接資料庫

#------------------- 取得環境變數內的敏感資料 --------------------
load_dotenv()
db_pwd = os.getenv("DB_PASSWORD") # 資料庫密碼

con = mysql.connector.connect(
            user="root",
            password=db_pwd,
            host="localhost",
            database="taipei_attractions"
        )
print("資料庫連線完成")

with open('data/taipei-attractions.json', 'r', encoding='utf-8') as file:
    raw_data = json.load(file)
    data = raw_data.get("result").get("results")
    image_regex = re.compile(r"https:\/\/www.travel.taipei\/[^\"\s]*?\.[jJ][pP][gG]", re.IGNORECASE)
    cursor = con.cursor()
    attraction_count = 0
    image_count = 0

    try:
        for idx, info in enumerate(data, 1):
            id = info.get("_id")
            name = info.get("name")
            category = info.get("CAT")
            description = info.get("description")
            address = info.get("address")
            transport = info.get("direction")
            mrt = info.get("MRT")
            lat = info.get("latitude")
            lng = info.get("longitude")
            urls = info.get("file")

            # 除了URL外的資訊
            cursor.execute(
                """INSERT INTO attractions (id, name, category, description, address, transport, mrt, lat, lng)
                VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)""",(id, name, category, description, address, transport, mrt, lat, lng)
                )
            attraction_count += 1

            # 插入URL
            images = image_regex.findall(urls)
            for image in images:
                cursor.execute(
                    """INSERT INTO attractions_images (attraction_id, image_url)
                    VALUES (%s,%s)""",(id, image)
                    )
                image_count += 1
                
            if idx % 10 == 0:
                print(f"已處理 {idx} 筆景點，{image_count} 張圖片")

        con.commit()
        print(f"\n✅ 匯入完成")
        print(f"景點：{attraction_count} 筆")
        print(f"圖片：{image_count} 張")

    except Exception as e:
        print(f"❌ 處理第 {idx} 筆（{name}）時失敗: {str(e)}")
        con.rollback()

    finally:
        cursor.close()
        con.close()