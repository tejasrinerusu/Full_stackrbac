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


def test_create_user_has_role(db: Session) -> None:
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

    test_role = crud.rbac.create_role(db, role_name="test")

    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/user-has-role",
        json={"user_id": str(user.id), "role_id": str(test_role.id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 201
    assert "user_id" in res
    assert "role_id" in res
    assert res["user_id"] == str(user.id)
    assert res["role_id"] == str(test_role.id)


def test_create_user_has_role_invalid_user_id(db: Session) -> None:
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
    r = client.post(
        "/api/v1/rbac/user-has-role",
        json={"user_id": str(uuid), "role_id": str(role.id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user not found"
    assert res["error"] == f"no user id: {uuid}"


def test_create_user_has_role_invalid_role_id(db: Session) -> None:
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
    r = client.post(
        "/api/v1/rbac/user-has-role",
        json={"user_id": str(user.id), "role_id": str(uuid)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_create_duplicate_user_has_role(db: Session) -> None:
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
    r = client.post(
        "/api/v1/rbac/user-has-role",
        json={"user_id": str(user.id), "role_id": str(role.id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 400
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user has role has already been created"
    assert res["error"] == f"user id: {user.id}, role id: {role.id}"


def test_read_user_has_roles(db: Session) -> None:
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
    r = client.get(f"/api/v1/rbac/user-has-role/{user.id}", headers=header)
    res = r.json()
    assert r.status_code == 200
    assert len(res) == 1
    assert res[0]["id"] == str(role.id)
    assert res[0]["name"] == str("admin")


def test_update_user_has_role(db: Session) -> None:
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

    test_role = crud.rbac.create_role(db, role_name="test")

    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/user-has-role/{user.id}",
        json={
            "old_role_id": str(role.id),
            "new_role_id": str(test_role.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 200
    assert "user_id" in res
    assert "role_id" in res
    assert res["user_id"] == str(user.id)
    assert res["role_id"] == str(test_role.id)


def test_update_user_has_role_invalid_user_id(db: Session) -> None:
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

    test_role = crud.rbac.create_role(db, role_name="test")

    uuid = uuid4()
    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/user-has-role/{uuid}",
        json={
            "old_role_id": str(role.id),
            "new_role_id": str(test_role.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user not found"
    assert res["error"] == f"no user id: {uuid}"


def test_update_user_has_role_invalid_role_id(db: Session) -> None:
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

    uuid = uuid4()
    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/user-has-role/{user.id}",
        json={
            "old_role_id": str(role.id),
            "new_role_id": str(uuid),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_update_not_found_user_has_role(db: Session) -> None:
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

    test_role = crud.rbac.create_role(db, role_name="test")

    uuid = uuid4()
    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/user-has-role/{user.id}",
        json={
            "old_role_id": str(uuid),
            "new_role_id": str(test_role.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user has role not found"
    assert res["error"] == f"no user id: {user.id}, role id: {uuid}"


def test_delete_not_found_user_has_role(db: Session) -> None:
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
    r = client.delete(f"/api/v1/rbac/user-has-role/{uuid}/{role.id}", headers=header)
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "user has role not found"
    assert res["error"] == f"no user id: {uuid}, role id: {role.id}"


def test_delete_user_has_role(db: Session) -> None:
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
    r = client.delete(f"/api/v1/rbac/user-has-role/{user.id}/{role.id}", headers=header)
    assert r.status_code == 204
