from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import RoleCreate, RoleOut
from utils.auth import verify_permission
from utils.exception import UvicornException


router = APIRouter()


@router.post("", response_model=RoleOut, status_code=201)
async def create_role(
    role: RoleCreate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.create"])
    db_obj = crud.rbac.get_role_by_name(db, name=role.name)
    if db_obj:
        raise UvicornException(
            status_code=400,
            message="role has already been created",
            error=f"role id: {db_obj.id}, role name: {db_obj.name}",
        )
    return crud.rbac.create_role(db, role_name=role.name)


@router.get("", response_model=list[RoleOut], status_code=200)
async def read_roles(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.read"])
    return crud.rbac.get_roles(db)


@router.patch("/{id}", response_model=RoleOut, status_code=200)
async def update_role(
    id: UUID,
    role: RoleCreate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.update"])
    db_obj = crud.rbac.get_role_by_id(db, role_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {id}",
        )
    return crud.rbac.update_role(db, role=db_obj, new_role_name=role.name)


@router.delete("/{id}", status_code=204)
async def delete_role(
    id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    await verify_permission(db, authorization, permissions=["setting.delete"])
    db_obj = crud.rbac.get_role_by_id(db, role_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {id}",
        )
    crud.rbac.delete_role(db, role=db_obj)
