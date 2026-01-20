# ------------ week 1 - attraction類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db # 記得從連線那邊引入連線的函式
from services.attraction_services import get_attraction_from_db, search_attractions, get_categories_from_db, get_mrts_from_db

router = APIRouter(prefix="/api", tags=["attractions"])
# prefix代表所有這邊的路由前面都會自動加上"/api"
# tag就只是一個幫助辨識的標籤，沒有實質作用

@router.get("/attractions")
async def api_search_attractions(
	page:int = Query(0,ge=0),
	category: Optional[str] = Query(None), 
	keyword: Optional[str] = Query(None),
	cnx=Depends(get_db)
):
	page_size = 8

	try:
		attractions_data = search_attractions(page, page_size, keyword, category, cnx)
		return attractions_data

	except Exception as e:
		print(f"❌ 執行失敗: {str(e)}")
		return JSONResponse(
			status_code=500,
			content={
				"error": True,
				"message": f" /api/attractions 伺服器內部錯誤:{str(e)}"
			}
		)


@router.get("/attraction/{attractionsId}")
async def attractions_by_id(attractionsId:int, cnx=Depends(get_db)):
	cursor = cnx.cursor(dictionary=True) #抓資訊
	try:
		attraction = get_attraction_from_db(attractionsId, cursor)

		if not attraction:
			return JSONResponse(
				status_code=400,
				content={
					"error": True,
					"message": "景點編號查無資料"
				}
			)

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
	try :
		categories = get_categories_from_db(cnx)

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

@router.get("/mrts")
async def list_mrts(cnx=Depends(get_db)):
	try :
		mrts =  get_mrts_from_db(cnx)
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