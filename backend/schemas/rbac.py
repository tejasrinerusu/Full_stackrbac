from uuid import UUID

from pydantic import BaseModel, EmailStr

# Properties to receive via API on creation
class UserCreate(BaseModel):
    email: EmailStr
    password: str


class UserOut(BaseModel):
    id: UUID
    email: EmailStr

    class Config:
        orm_mode = True


class UserUpdate(BaseModel):
    email: EmailStr


class UserHasRole(BaseModel):
    user_id: UUID
    role_id: UUID

    class Config:
        orm_mode = True


class UserHasRoleUpdate(BaseModel):
    old_role_id: UUID
    new_role_id: UUID


class PermissionCreate(BaseModel):
    name: str


class PermissionOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class RoleCreate(BaseModel):
    name: str


class RoleOut(BaseModel):
    id: UUID
    name: str

    class Config:
        orm_mode = True


class RoleHasPermission(BaseModel):
    role_id: UUID
    permission_id: UUID

    class Config:
        orm_mode = True


class RoleHasPermissionUpdate(BaseModel):
    old_permission_id: UUID
    new_permission_id: UUID
