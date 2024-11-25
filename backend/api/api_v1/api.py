from fastapi import APIRouter

from api.api_v1.endpoints import (
    auth,
    permission,
    role,
    role_has_permission,
    user,
    user_has_role,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(permission.router, prefix="/rbac/permission", tags=["rbac"])
api_router.include_router(role.router, prefix="/rbac/role", tags=["rbac"])
api_router.include_router(
    role_has_permission.router, prefix="/rbac/role-has-permission", tags=["rbac"]
)
api_router.include_router(user.router, prefix="/rbac/user", tags=["rbac"])
api_router.include_router(
    user_has_role.router, prefix="/rbac/user-has-role", tags=["rbac"]
)
