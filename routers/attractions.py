# ------------ week 1 - attraction類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
import json
from database.connection import get_db # 記得從連線那邊引入連線的函式

router = APIRouter(prefix="/api", tags=["attractions"])
# prefix代表所有這邊的路由前面都會自動加上"/api"
# tag就只是一個幫助辨識的標籤，沒有實質作用

@router.get("/attractions")
async def search_attractions(
	page:int = Query(0,ge=0),
	category: Optional[str] = Query(None), 
	keyword: Optional[str] = Query(None),
	cnx=Depends(get_db)
):
	page_size = 8
	cursor = cnx.cursor(dictionary=True)
    
	try:
		offset = page * page_size

		# 動態構造 WHERE 條件
		conditions = []
		params = []
        
		if category:
			conditions.append("a.category=%s")
			params.append(category)

		if keyword:
			conditions.append("(a.mrt=%s OR a.name REGEXP %s)")
			params.extend([keyword, keyword])

		# 動態構造出條件
		where_clause = " AND ".join(conditions) if conditions else "1=1"

		sql = f"""
		SELECT 
			a.id,
			a.name,
			a.category,
			a.description,
			a.address,
			a.transport,
			a.mrt,
			a.lat,
			a.lng,
			GROUP_CONCAT(ai.image_url) AS images
		FROM attractions a 
		LEFT JOIN attractions_images ai
		ON a.id = ai.attraction_id
		WHERE {where_clause}
		GROUP BY a.id
		LIMIT 8 OFFSET {offset}"""

		cursor.execute(sql, tuple(params))
		result = cursor.fetchall()

		for row in result:
			image_str = row.get("images",'')
			row['images'] = image_str.split(',') if image_str else []


		# 確認是否有下一頁
		check_next_page = f"""SELECT * FROM attractions a
		WHERE {where_clause}
		LIMIT 1 OFFSET {(page+1)* page_size}"""

		cursor.execute(check_next_page, tuple(params))
		has_next_page = len(cursor.fetchall()) > 0
		nextPage = (page + 1) if has_next_page else None

		context = {
			"nextPage": nextPage,
			"data": result,	
		}

		return context

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f" /api/attractions 伺服器內部錯誤:{str(e)}"
			}
		)
    
	finally:
		cursor.close()

@router.get("/attraction/{attractionsId}")
async def attractions_by_id(attractionsId:int, cnx=Depends(get_db)):
	cursor = cnx.cursor(dictionary=True) #抓資訊
	try:
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
			,(attractionsId,)) # 單元素tuple結尾括號前要記得加逗號，不然python無法判斷這是tuple還是普通字串
		attraction = cursor.fetchone()

		if not attraction:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "景點編號查無資料"
				}
			)
		
		if isinstance(attraction['images'], str): # 如果是字串
			attraction['images'] = json.loads(attraction['images']) # 轉成陣列

		return {"data": attraction}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)
    
	finally:
		cursor.close()

@router.get("/categories")
async def list_categories(cnx=Depends(get_db)):
	cursor = cnx.cursor()
	try :
		cursor.execute(
			"""SELECT DISTINCT category 
			FROM attractions 
			ORDER BY category DESC""")
		result = cursor.fetchall()
		categories = [category[0] for category in result]

		return {"data": categories}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)

	finally:
		cursor.close()

@router.get("/mrts")
async def list_mrts(cnx=Depends(get_db)):
	cursor = cnx.cursor()
	try :
		cursor.execute(
			"""SELECT mrt, COUNT(*)AS num 
			FROM attractions 
			WHERE mrt IS NOT NULL AND mrt !=''
			GROUP BY mrt ORDER BY num DESC;""")
			# SQL中判斷 NULL 需要要用 IS NULL 或 IS NOT NULL
		result = cursor.fetchall()
		mrts = [mrt[0] for mrt in result]
		return {"data": mrts}

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f"伺服器內部錯誤:{str(e)}"
			}
		)

	finally:
		cursor.close()