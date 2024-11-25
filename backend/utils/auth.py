from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.api_v1.endpoints import auth
from schemas.token import Token
from utils.exception import UvicornException


async def verify_permission(
    db: Session, authorization: str | None, permissions: list[str]
) -> bool:
    if not authorization or not authorization.startswith("Bearer "):
        raise UvicornException(
            status_code=401,
            message="user is not authorized",
            error="header does not start with Bearer",
        )
    token = authorization.split("Bearer ")[1]
    res = await auth.auth(Token(permissions=permissions, token=token), db=db)
    if type(res) == JSONResponse and res.status_code == 401:
        raise UvicornException(
            status_code=401,
            message="user is not authorized",
            error="user does not have permission",
        )
    return True
