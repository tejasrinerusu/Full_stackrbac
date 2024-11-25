from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import PermissionCreate, PermissionOut
from utils.auth import verify_permission
from utils.exception import UvicornException


router = APIRouter()


@router.post("", response_model=PermissionOut, status_code=201)
async def create_permission(
    permission: PermissionCreate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.create"])
    db_obj = crud.rbac.get_permission_by_name(db, name=permission.name)
    if db_obj:
        raise UvicornException(
            status_code=400,
            message="permission has already been created",
            error=f"permission id: {db_obj.id}, permission name: {db_obj.name}",
        )
    return crud.rbac.create_permissions(db, permissions=[permission.name])[0]


@router.get("", response_model=list[PermissionOut], status_code=200)
async def read_permissions(
    authorization: str | None = Header(default=None), db: Session = Depends(get_db)
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.read"])
    return crud.rbac.get_permissions(db)


@router.patch("/{id}", response_model=PermissionOut, status_code=200)
async def update_permission(
    id: UUID,
    permission: PermissionCreate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.update"])
    db_obj = crud.rbac.get_permission_by_id(db, permission_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="permission not found",
            error=f"no permission id: {id}",
        )
    return crud.rbac.update_permission(
        db, permission=db_obj, new_permission_name=permission.name
    )


@router.delete("/{id}", status_code=204)
async def delete_permission(
    id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    await verify_permission(db, authorization, permissions=["setting.delete"])
    db_obj = crud.rbac.get_permission_by_id(db, permission_id=id)
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="permission not found",
            error=f"no permission id: {id}",
        )
    crud.rbac.delete_permission(db, permission=db_obj)
