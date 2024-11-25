from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from main import app
from schemas.rbac import UserCreate
from tests.conftest import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_create_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    new_email = "test@test.com"
    new_password = "12345678"
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/user",
        json={"email": new_email, "password": new_password},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 201
    assert "id" in res
    assert "email" in res
    assert res["email"] == new_email


def test_create_duplicate_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    new_email = "admin@test.com"
    new_password = "12345678"
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/user",
        json={"email": new_email, "password": new_password},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 400
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user has already been created"


def test_read_users(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    header = {"authorization": f"Bearer {res['token']}"}
    r = client.get("/api/v1/rbac/user", headers=header)
    res = r.json()
    assert r.status_code == 200
    assert len(res) == 1
    assert "id" in res[0]
    assert "email" in res[0]
    assert res[0]["id"] == str(user.id)
    assert res[0]["email"] == email


def test_update_not_found_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    uuid = uuid4()
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.patch(
        f"/api/v1/rbac/user/{uuid}", json={"email": "test@test.com"}, headers=header
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user not found"
    assert res["error"] == f"no user id: {uuid}"


def test_update_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    token = res["token"]

    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/user/{user.id}",
        json={"email": "test@test.com"},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 200
    assert "id" in res
    assert "email" in res
    assert res["id"] == str(user.id)
    assert res["email"] == "test@test.com"


def test_delete_not_found_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    uuid = uuid4()
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.delete(f"/api/v1/rbac/user/{uuid}", headers=header)
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user not found"
    assert res["error"] == f"no user id: {uuid}"


def test_delete_user_without_forign_key_constraint(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )
    test_user = UserCreate(email="test@test.com", password=password)
    crud.rbac.create_user(db, obj_in=test_user)

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    token = res["token"]

    header = {"authorization": f"Bearer {token}"}
    r = client.get("/api/v1/rbac/user", headers=header)
    res = r.json()
    for user in res:
        if user["email"] == "test@test.com":
            user_id = user["id"]
            break

    r = client.delete(f"/api/v1/rbac/user/{user_id}", headers=header)
    assert r.status_code == 204


def test_delete_user_with_forign_key_constraint(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    token = res["token"]

    header = {"authorization": f"Bearer {token}"}
    r = client.delete(
        f"/api/v1/rbac/user/{user.id}",
        headers=header,
    )
    assert r.status_code == 204
