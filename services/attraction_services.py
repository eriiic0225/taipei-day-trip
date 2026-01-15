import json

def get_attraction_from_db(id:int, cursor):
    cursor.execute(
			"""SELECT 
				a.id, 
				a.name,
				a.category,
				a.description, 
				a.address, 
				a.transport, 
				a.mrt, 
				a.lat, 
				a.lng,
				JSON_ARRAYAGG(ai.image_url) AS images 
			FROM attractions a 
			LEFT JOIN attractions_images ai
			ON a.id = ai.attraction_id
			WHERE a.id=%s
			GROUP BY a.id"""
			,(id,)) # 單元素tuple結尾括號前要記得加逗號，不然python無法判斷這是tuple還是普通字串
    attraction = cursor.fetchone()

    if attraction and isinstance(attraction['images'], str): # 如果是字串
        attraction['images'] = json.loads(attraction['images']) # 轉成陣列

    return attraction