import json

def search_attractions(
		page: int, 
		page_size: int, 
		keyword: str | None, 
		category: str | None, 
		cnx):
	cursor = None
	try:
		cursor = cnx.cursor(dictionary=True)
		offset = page * page_size

		# 1. 動態構造 WHERE 條件
		conditions = []
		params = []
        
		if category:
			conditions.append("a.category=%s")
			params.append(category)

		if keyword:
			conditions.append("(a.mrt=%s OR a.name REGEXP %s)")
			params.extend([keyword, keyword])

		where_clause = " AND ".join(conditions) if conditions else "1=1"

		# 2. 主要的資料查詢
		sql = f"""
			SELECT 
			a.id, a.name, a.category, a.description, a.address,
			a.transport, a.mrt, a.lat, a.lng,
			GROUP_CONCAT(ai.image_url) AS images
			FROM attractions a 
			LEFT JOIN attractions_images ai ON a.id = ai.attraction_id
			WHERE {where_clause}
			GROUP BY a.id
			LIMIT %s OFFSET %s"""

		query_params = tuple(params) + (page_size, offset) # tuple連接只能用 +不能用 append
		cursor.execute(sql, query_params)
		result = cursor.fetchall()

		for row in result:
			image_str = row.get("images",'')
			row['images'] = image_str.split(',') if image_str else []

		# 3. 檢查是否有下一頁
		check_sql = f"""
		SELECT 1 FROM attractions a
		WHERE {where_clause}
		LIMIT 1 OFFSET %s"""

		check_params = tuple(params) + ((page + 1) * page_size,)
		cursor.execute(check_sql, check_params)
		has_next_page = cursor.fetchone() is not None
		nextPage = (page + 1) if has_next_page else None

		return {
			"nextPage": nextPage,
			"data": result
		}
	finally:
		if cursor:
			cursor.close()


def get_attraction_from_db(id: int, cnx):
	cursor = None
	try:
		cursor = cnx.cursor(dictionary=True)
		cursor.execute(
			"""SELECT 
				a.id, a.name, a.category, a.description, a.address, 
				a.transport, a.mrt, a.lat, a.lng,
				JSON_ARRAYAGG(ai.image_url) AS images 
			FROM attractions a 
			LEFT JOIN attractions_images ai ON a.id = ai.attraction_id
			WHERE a.id=%s
			GROUP BY a.id""",
			(id,)
		)
		attraction = cursor.fetchone()

		# 因為GROUP_CONCAT和JSON_ARRAYAGG回傳的是字串，
		# 需要手動解析成前端期望的JSON陣列格式。
		if attraction and isinstance(attraction['images'], str):
			attraction['images'] = json.loads(attraction['images'])

		return attraction
	finally:
		if cursor:
			cursor.close()

def get_categories_from_db(cnx):
	cursor = None
	try:
		cursor = cnx.cursor()
		cursor.execute(
			"""SELECT DISTINCT category 
			FROM attractions 
			ORDER BY category DESC""")
		result = cursor.fetchall()
		categories = [category[0] for category in result]
		return categories
	finally:
		if cursor:
			cursor.close()

def get_mrts_from_db(cnx):
	"""
	從資料庫取得所有不重複的捷運站列表，並依景點數量排序。
	"""
	cursor = None
	try:
		cursor = cnx.cursor()
		cursor.execute(
			"""SELECT mrt, COUNT(*) AS num 
			FROM attractions 
			WHERE mrt IS NOT NULL AND mrt !=''
			GROUP BY mrt ORDER BY num DESC;""")
			# SQL中判斷 NULL 需要要用 IS NULL 或 IS NOT NULL
		result = cursor.fetchall()
		mrts = [mrt[0] for mrt in result]
		return mrts
	finally:
		if cursor:
			cursor.close()