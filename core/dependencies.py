# FastAPI 依賴
# 供路由使用的依賴函數。當路由需要驗證 token 時，直接用這個
from fastapi import Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from services.user_service import decode_access_token
from models.user import TokenPayload

bearer_scheme = HTTPBearer(auto_error=False)

async def verify_token(
        credentials: HTTPAuthorizationCredentials = Security(bearer_scheme)
        ):
    """
    驗證 HTTP Bearer token
    """
    # 如果前端沒有傳來token
    if credentials is None:
        return None
    # 抓取token本體
    token = credentials.credentials
    # 由 service.py 的函式做解析
    payload = decode_access_token(token) #這裡會取得解析好的payload(TokenPayload物件)
    
    return payload