from typing import Any
from uuid import UUID

from fastapi import APIRouter, Depends, Header
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from schemas.rbac import RoleOut, UserHasRole, UserHasRoleUpdate
from utils.auth import verify_permission
from utils.exception import UvicornException


router = APIRouter()


@router.post("", response_model=UserHasRole, status_code=201)
async def create_user_has_role(
    user_has_role: UserHasRole,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.create"])
    if crud.rbac.get_user_by_id(db, user_id=user_has_role.user_id) is None:
        raise UvicornException(
            status_code=404,
            message="user not found",
            error=f"no user id: {user_has_role.user_id}",
        )
    if crud.rbac.get_role_by_id(db, role_id=user_has_role.role_id) is None:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {user_has_role.role_id}",
        )
    db_obj = crud.rbac.get_user_has_role_by_user_id_and_role_id(
        db,
        user_id=user_has_role.user_id,
        role_id=user_has_role.role_id,
    )
    if db_obj:
        raise UvicornException(
            status_code=400,
            message="user has role has already been created",
            error=f"user id: {db_obj.user_id}, role id: {db_obj.role_id}",
        )
    return crud.rbac.create_user_has_role(
        db,
        user_id=user_has_role.user_id,
        role_id=user_has_role.role_id,
    )


@router.get("/{id}", response_model=list[RoleOut], status_code=200)
async def read_user_has_roles(
    id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.read"])
    db_objs = crud.rbac.get_all_user_has_role_by_user_id(db, user_id=id)
    return [crud.rbac.get_role_by_id(db, role_id=db_obj.role_id) for db_obj in db_objs]


@router.patch("/{id}", response_model=UserHasRole, status_code=200)
async def update_user_has_role(
    id: UUID,
    role_update: UserHasRoleUpdate,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> Any:
    await verify_permission(db, authorization, permissions=["setting.update"])
    if crud.rbac.get_user_by_id(db, user_id=id) is None:
        raise UvicornException(
            status_code=404,
            message="user not found",
            error=f"no user id: {id}",
        )
    if crud.rbac.get_role_by_id(db, role_id=role_update.new_role_id) is None:
        raise UvicornException(
            status_code=404,
            message="role not found",
            error=f"no role id: {role_update.new_role_id}",
        )
    db_obj = crud.rbac.get_user_has_role_by_user_id_and_role_id(
        db,
        user_id=id,
        role_id=role_update.old_role_id,
    )
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="user has role not found",
            error=f"no user id: {id}, role id: {role_update.old_role_id}",
        )
    return crud.rbac.update_user_has_role(
        db, user_has_role=db_obj, new_role=role_update.new_role_id
    )


@router.delete("/{user_id}/{role_id}", status_code=204)
async def delete_user_has_role(
    user_id: UUID,
    role_id: UUID,
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
):
    await verify_permission(db, authorization, permissions=["setting.delete"])
    db_obj = crud.rbac.get_user_has_role_by_user_id_and_role_id(
        db, user_id=user_id, role_id=role_id
    )
    if not db_obj:
        raise UvicornException(
            status_code=404,
            message="user has role not found",
            error=f"no user id: {user_id}, role id: {role_id}",
        )
    crud.rbac.delete_user_has_role(db, user_has_role=db_obj)
