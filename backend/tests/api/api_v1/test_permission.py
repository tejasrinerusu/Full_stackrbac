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


def test_create_permission(db: Session) -> None:
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

    permission_name = "test.create"
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/permission", json={"name": permission_name}, headers=header
    )
    res = r.json()
    assert r.status_code == 201
    assert "id" in res
    assert "name" in res
    assert res["name"] == permission_name


def test_create_duplicate_permission(db: Session) -> None:
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

    permission_name = "test.create"
    header = {"authorization": f"Bearer {res['token']}"}
    r1 = client.post(
        "/api/v1/rbac/permission", json={"name": permission_name}, headers=header
    )
    res1 = r1.json()

    r2 = client.post(
        "/api/v1/rbac/permission", json={"name": permission_name}, headers=header
    )
    res2 = r2.json()
    assert r2.status_code == 400
    assert "message" in res2
    assert "error" in res2
    assert res2["message"] == "permission has already been created"
    assert (
        res2["error"] == f"permission id: {res1['id']}, permission name: {res1['name']}"
    )


def test_create_permission_without_permission(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.read", "setting.update", "setting.delete"]
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

    permission_name = "test.create"
    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/permission", json={"name": permission_name}, headers=header
    )
    res = r.json()
    assert r.status_code == 401
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user is not authorized"
    assert res["error"] == "user does not have permission"


def test_create_permission_without_authorization() -> None:
    permission_name = "test.create"
    r = client.post("/api/v1/rbac/permission", json={"name": permission_name})
    res = r.json()
    assert r.status_code == 401
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user is not authorized"
    assert res["error"] == "header does not start with Bearer"


def test_create_permission_with_wrong_authorization() -> None:
    permission_name = "test.create"
    header = {"authorization": ""}
    r = client.post(
        "/api/v1/rbac/permission", json={"name": permission_name}, headers=header
    )
    res = r.json()
    assert r.status_code == 401
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user is not authorized"
    assert res["error"] == "header does not start with Bearer"


def test_read_permissions(db: Session) -> None:
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
    r = client.get("/api/v1/rbac/permission", headers=header)
    res = r.json()
    assert r.status_code == 200
    for idx, permission in enumerate(res):
        assert permission["id"] == str(db_objs[idx].id)
        assert permission["name"] == db_objs[idx].name


def test_update_not_found_permission(db: Session) -> None:
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
        f"/api/v1/rbac/permission/{uuid}", json={"name": "test.update"}, headers=header
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "permission not found"
    assert res["error"] == f"no permission id: {uuid}"


def test_update_permission(db: Session) -> None:
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
    r = client.get("/api/v1/rbac/permission", headers=header)
    res = r.json()
    for permission in res:
        if permission["name"] == "setting.update":
            permission_id = permission["id"]
            break

    r = client.patch(
        f"/api/v1/rbac/permission/{permission_id}",
        json={"name": "test.update"},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 200
    assert "id" in res
    assert "name" in res
    assert res["id"] == permission_id
    assert res["name"] == "test.update"


def test_delete_not_found_permission(db: Session) -> None:
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
    r = client.delete(f"/api/v1/rbac/permission/{uuid}", headers=header)
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "permission not found"
    assert res["error"] == f"no permission id: {uuid}"


def test_delete_permission_without_forign_key_constraint(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = [
        "setting.create",
        "setting.read",
        "setting.update",
        "setting.delete",
        "test.delete",
    ]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)
    role = crud.rbac.create_role(db, role_name="admin")
    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)
    db_objs = crud.rbac.create_permissions(db, permissions=permissions)
    crud.rbac.create_role_has_permission(
        db, role_id=role.id, permission_ids=[obj.id for obj in db_objs[:-1]]
    )

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    token = res["token"]

    header = {"authorization": f"Bearer {token}"}
    r = client.get("/api/v1/rbac/permission", headers=header)
    res = r.json()
    for permission in res:
        if permission["name"] == "test.delete":
            permission_id = permission["id"]
            break

    r = client.delete(
        f"/api/v1/rbac/permission/{permission_id}",
        headers=header,
    )
    assert r.status_code == 204


def test_delete_permission_with_forign_key_constraint(db: Session) -> None:
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
    r = client.get("/api/v1/rbac/permission", headers=header)
    res = r.json()
    for permission in res:
        if permission["name"] == "setting.delete":
            permission_id = permission["id"]
            break

    r = client.delete(
        f"/api/v1/rbac/permission/{permission_id}",
        headers=header,
    )
    assert r.status_code == 204
