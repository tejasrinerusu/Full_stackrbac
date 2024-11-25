from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import PermissionOut, RoleHasPermission, RoleHasPermissionUpdate
from utils.auth import verify_permission
from utils.exception import UvicornException


router = APIRouter()


@router.post("", response_model=RoleHasPermission, status_code=201)
async def create_role_has_permission(
    role_has_permission: RoleHasPermission,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.create"])
    if crud.rbac.get_role_by_id(db, role_id=role_has_permission.role_id) is None:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {role_has_permission.role_id}",
        )
    if (
        crud.rbac.get_permission_by_id(
            db, permission_id=role_has_permission.permission_id
        )
        is None
    ):
        raise UvicornException(
            status_code=404,
            message="permission not found",
            error=f"no permission id: {role_has_permission.permission_id}",
        )
    db_obj = crud.rbac.get_role_has_permission_by_role_id_and_permission_id(
        db,
        role_id=role_has_permission.role_id,
        permission_id=role_has_permission.permission_id,
    )
    if db_obj:
        raise UvicornException(
            status_code=400,
            message="role has permission has already been created",
            error=f"no role id: {db_obj.role_id}, permission id: {db_obj.permission_id}",
        )
    return crud.rbac.create_role_has_permission(
        db,
        role_id=role_has_permission.role_id,
        permission_ids=[role_has_permission.permission_id],
    )[0]


@router.get("/{id}", response_model=list[PermissionOut], status_code=200)
async def read_role_has_permissions(
    id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.read"])
    db_objs = crud.rbac.get_all_role_has_permission_by_role_id(db, role_id=id)
    return [
        crud.rbac.get_permission_by_id(db, permission_id=db_obj.permission_id)
        for db_obj in db_objs
    ]


@router.patch("/{id}", response_model=RoleHasPermission, status_code=200)
async def update_role_has_permission(
    id: UUID,
    permission_update: RoleHasPermissionUpdate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.update"])
    if crud.rbac.get_role_by_id(db, role_id=id) is None:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {id}",
        )
    if (
        crud.rbac.get_permission_by_id(
            db, permission_id=permission_update.new_permission_id
        )
        is None
    ):
        raise UvicornException(
            status_code=404,
            message="permission not found",
            error=f"no permission id: {permission_update.new_permission_id}",
        )
    db_obj = crud.rbac.get_role_has_permission_by_role_id_and_permission_id(
        db,
        role_id=id,
        permission_id=permission_update.old_permission_id,
    )
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="role has permission not found",
            error=f"no role id: {id}, permission id: {permission_update.old_permission_id}",
        )
    return crud.rbac.update_role_has_permission(
        db,
        role_has_permission=db_obj,
        new_permission=permission_update.new_permission_id,
    )


@router.delete("/{role_id}/{permission_id}", status_code=204)
async def delete_role_has_permission(
    role_id: UUID,
    permission_id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    await verify_permission(db, authorization, permissions=["setting.delete"])
    db_obj = crud.rbac.get_role_has_permission_by_role_id_and_permission_id(
        db,
        role_id=role_id,
        permission_id=permission_id,
    )
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="role has permission not found",
            error=f"no role id: {role_id}, permission id: {permission_id}",
        )
    crud.rbac.delete_role_has_permission(db, role_has_permission=db_obj)
