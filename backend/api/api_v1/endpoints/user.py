from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import UserCreate, UserOut, UserUpdate
from utils.auth import verify_permission
from utils.exception import UvicornException


router = APIRouter()


@router.post("", response_model=UserOut, status_code=201)
async def create_user(
    user: UserCreate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.create"])
    db_obj = crud.rbac.get_user_by_email(db, email=user.email)
    if db_obj:
        raise UvicornException(
            status_code=400,
            message="user has already been created",
            error=f"user id: {db_obj.id}, user email: {db_obj.email}",
        )
    return crud.rbac.create_user(db, obj_in=user)


@router.get("", response_model=list[UserOut], status_code=200)
async def read_users(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.read"])
    return crud.rbac.get_users(db)


@router.patch("/{id}", response_model=UserOut, status_code=200)
async def update_user(
    id: UUID,
    user: UserUpdate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.update"])
    db_obj = crud.rbac.get_user_by_id(db, user_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="user not found",
            error=f"no user id: {id}",
        )
    return crud.rbac.update_user(db, user=db_obj, new_email=user.email)


@router.delete("/{id}", status_code=204)
async def delete_user(
    id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    await verify_permission(db, authorization, permissions=["setting.delete"])
    db_obj = crud.rbac.get_user_by_id(db, user_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="user not found",
            error=f"no user id: {id}",
        )
    crud.rbac.delete_user(db, user=db_obj)
