from fastapi.encoders import jsonable_encoder
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from crud import rbac
from main import app
from schemas.rbac import UserCreate


client = TestClient(app)


# User
def test_create_user(db: Session) -> None:
    email = "random@test.com"
    password = "secret"
    user_in = UserCreate(email=email, password=password)
    user = rbac.create_user(db, obj_in=user_in)
    assert user.email == email
    assert hasattr(user, "hashed_password")


# Role
def test_create_role(db: Session) -> None:
    role_name = "admin"
    role = rbac.create_role(db, role_name=role_name)
    assert role.name == role_name


def test_get_role_by_name(db: Session) -> None:
    role_name = "admin"
    role1 = rbac.create_role(db, role_name=role_name)
    role2 = rbac.get_role_by_name(db, name=role_name)
    assert role2
    assert role2.name == role1.name
    assert jsonable_encoder(role1) == jsonable_encoder(role2)


# RoleHasPermission
def test_create_role_has_permission(db: Session) -> None:
    role_name = "admin"
    role = rbac.create_role(db, role_name=role_name)

    permissions = ["permission1", "permission2", "permission3"]
    db_objs = rbac.create_permissions(db, permissions=permissions)
    permission_ids = [db_obj.id for db_obj in db_objs]

    role_has_permissions = rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=permission_ids
    )
    for i, db_obj in enumerate(role_has_permissions):
        assert db_obj.role_id == role.id
        assert db_obj.permission_id == permission_ids[i]


# UserHasRole
def test_create_user_has_role(db: Session) -> None:
    email = "random@test.com"
    password = "secret"
    user_in = UserCreate(email=email, password=password)
    user = rbac.create_user(db, obj_in=user_in)

    role_name = "admin"
    role = rbac.create_role(db, role_name=role_name)

    user_has_role = rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    assert user_has_role.user_id == user.id
    assert user_has_role.role_id == role.id


# Permission
def test_create_permission(db: Session) -> None:
    permissions = ["permission1"]
    db_objs = rbac.create_permissions(db, permissions=permissions)
    for i, db_obj in enumerate(db_objs):
        assert db_obj.name == permissions[i]


def test_create_permissions(db: Session) -> None:
    permissions = ["permission1", "permission2", "permission3"]
    db_objs = rbac.create_permissions(db, permissions=permissions)
    for i, db_obj in enumerate(db_objs):
        assert db_obj.name == permissions[i]
