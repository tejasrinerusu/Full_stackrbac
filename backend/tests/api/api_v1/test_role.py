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


def test_create_role(db: Session) -> None:
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

    role_name = "test"
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post("/api/v1/rbac/role", json={"name": role_name}, headers=header)
    res = r.json()
    assert r.status_code == 201
    assert "id" in res
    assert "name" in res
    assert res["name"] == role_name


def test_create_duplicate_role(db: Session) -> None:
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

    role_name = "test"
    header = {"authorization": f"Bearer {res['token']}"}
    r1 = client.post("/api/v1/rbac/role", json={"name": role_name}, headers=header)
    res1 = r1.json()

    r2 = client.post("/api/v1/rbac/role", json={"name": role_name}, headers=header)
    res2 = r2.json()
    assert r2.status_code == 400
    assert "message" in res2
    assert "error" in res2
    assert res2["message"] == "role has already been created"
    assert res2["error"] == f"role id: {res1['id']}, role name: {res1['name']}"


def test_read_roles(db: Session) -> None:
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
    r = client.get("/api/v1/rbac/role", headers=header)
    res = r.json()
    assert r.status_code == 200
    assert len(res) == 1
    assert "id" in res[0]
    assert "name" in res[0]
    assert res[0]["id"] == str(role.id)
    assert res[0]["name"] == "admin"


def test_update_not_found_role(db: Session) -> None:
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
    r = client.patch(f"/api/v1/rbac/role/{uuid}", json={"name": "test"}, headers=header)
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_update_role(db: Session) -> None:
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
    r = client.get("/api/v1/rbac/role", headers=header)
    res = r.json()
    for role in res:
        if role["name"] == "admin":
            role_id = role["id"]
            break

    r = client.patch(
        f"/api/v1/rbac/role/{role_id}",
        json={"name": "test"},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 200
    assert "id" in res
    assert "name" in res
    assert res["id"] == role_id
    assert res["name"] == "test"


def test_delete_not_found_role(db: Session) -> None:
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
    r = client.delete(f"/api/v1/rbac/role/{uuid}", headers=header)
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_delete_role_without_forign_key_constraint(db: Session) -> None:
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

    test_role = crud.rbac.create_role(db, role_name="test")

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    token = res["token"]

    header = {"authorization": f"Bearer {token}"}
    r = client.delete(
        f"/api/v1/rbac/role/{test_role.id}",
        headers=header,
    )
    assert r.status_code == 204


def test_delete_role_with_forign_key_constraint(db: Session) -> None:
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
        f"/api/v1/rbac/role/{role.id}",
        headers=header,
    )
    assert r.status_code == 204
