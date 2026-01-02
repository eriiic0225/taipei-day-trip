# FastAPI 依賴
# 供路由使用的依賴函數。當路由需要驗證 token 時，直接用這個
from fastapi import Header
from auth.service import decode_access_token
from auth.schemas import TokenPayload
from typing import Optional

async def verify_token(
        authorization: Optional[str] = Header(None)
        ) -> Optional[TokenPayload]:
    """
    驗證 HTTP Bearer token
    從 Authorization header 中提取 token
    """
    print(authorization)
    # 如果前端沒有傳來token
    if authorization is None:
        return None

    # 驗證 token 類型是否為 Bearer
    if not authorization.startswith("Bearer "):
        return None
    
    # 抓取token本體
    token = authorization.split(" ")[1]
    # 由 service.py 的函式做解析
    payload = decode_access_token(token) #這裡會取得解析好的payload(TokenPayload物件)
    
    return payload