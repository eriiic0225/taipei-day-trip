# ------------ week 1 - attraction類的API ------------
from fastapi import APIRouter, Query, Depends
from fastapi.responses import JSONResponse
from typing import Optional
from database.connection import get_db
from services.attraction_services import get_attraction_from_db, search_attractions, get_categories_from_db, get_mrts_from_db

router = APIRouter(prefix="/api", tags=["Attractions"])

@router.get("/attractions")
async def api_search_attractions(
	page:int = Query(0,ge=0),
	category: Optional[str] = Query(None), 
	keyword: Optional[str] = Query(None),
	cnx=Depends(get_db)
):
	try:
		attractions_data = search_attractions(page, 8, keyword, category, cnx)
		return attractions_data
	
	except Exception as e:
		return JSONResponse(status_code=500, content={"error": True, "message": str(e)})

@router.get("/attraction/{attractionId}")
async def api_get_attraction_by_id(attractionId:int, cnx=Depends(get_db)):
	try:
		attraction = get_attraction_from_db(attractionId, cnx)
		if not attraction:
			return JSONResponse(
				status_code=400,
				content={"error": True, "message": "景點編號不正確"}
			)
		return {"data": attraction}
	except Exception as e:
		return JSONResponse(status_code=500, content={"error": True, "message": str(e)})

@router.get("/categories")
async def api_list_categories(cnx=Depends(get_db)):
	try :
		categories = get_categories_from_db(cnx)
		return {"data": categories}
	except Exception as e:
		return JSONResponse(status_code=500, content={"error": True, "message": str(e)})

@router.get("/mrts")
async def api_list_mrts(cnx=Depends(get_db)):
	try :
		mrts =  get_mrts_from_db(cnx)
		return {"data": mrts}
	except Exception as e:
		return JSONResponse(status_code=500, content={"error": True, "message": str(e)})