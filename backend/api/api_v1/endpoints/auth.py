from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import UserCreate
from schemas.token import Token
from utils import security

router = APIRouter()


@router.post("/login", response_model=Token, status_code=201)
async def login(body: UserCreate, db: Session = Depends(get_db)) -> Any:
    user = crud.rbac.authenticate(db, obj_in=body)
    if not user:
        return JSONResponse(
            status_code=400, content={"message": "Incorrect email or password"}
        )
    role_ids = crud.rbac.get_all_role_ids_by_user_id(db, user_id=user.id)
    permission_ids = []
    for role_id in role_ids:
        permission_ids += crud.rbac.get_all_permission_ids_by_role_id(
            db, role_id=role_id
        )
    return {
        "permissions": [
            crud.rbac.get_permission_name_by_id(db, permission_id=permission_id)
            for permission_id in permission_ids
        ],
        "token": security.generate_jwt(permission_ids, user.email),
    }


@router.post("", status_code=201)
async def auth(body: Token, db: Session = Depends(get_db)) -> Any:
    payload = security.verify_jwt(body.token)
    permission_names = [
        crud.rbac.get_permission_name_by_id(db, permission_id=permission_id)
        for permission_id in payload["permissions"]
    ]
    for permission in body.permissions:
        if not permission in permission_names:
            return JSONResponse(
                status_code=401, content={"message": "user does not have permission"}
            )
    return {"message": "success"}
