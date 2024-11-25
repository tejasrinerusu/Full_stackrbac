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


def test_create_role_has_permission(db: Session) -> None:
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
    test_permission = crud.rbac.create_permissions(db, permissions=["test.test"])[0]

    header = {"authorization": f"Bearer {res['token']}"}
    r = client.post(
        "/api/v1/rbac/role-has-permission",
        json={"role_id": str(test_role.id), "permission_id": str(test_permission.id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 201
    assert "role_id" in res
    assert "permission_id" in res
    assert res["role_id"] == str(test_role.id)
    assert res["permission_id"] == str(test_permission.id)


def test_create_role_has_permission_invalid_role_id(db: Session) -> None:
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
        "/api/v1/rbac/role-has-permission",
        json={"role_id": str(uuid), "permission_id": str(db_objs[0].id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_create_role_has_permission_invalid_permission_id(db: Session) -> None:
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
        "/api/v1/rbac/role-has-permission",
        json={"role_id": str(role.id), "permission_id": str(uuid)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "permission not found"
    assert res["error"] == f"no permission id: {uuid}"


def test_create_duplicate_role_has_permission(db: Session) -> None:
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
        "/api/v1/rbac/role-has-permission",
        json={"role_id": str(role.id), "permission_id": str(db_objs[0].id)},
        headers=header,
    )
    res = r.json()
    assert r.status_code == 400
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role has permission has already been created"
    assert res["error"] == f"no role id: {role.id}, permission id: {db_objs[0].id}"


def test_read_role_has_permissions(db: Session) -> None:
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
    r = client.get(f"/api/v1/rbac/role-has-permission/{role.id}", headers=header)
    res = r.json()
    assert r.status_code == 200
    assert len(res) == 4
    for idx, permission in enumerate(res):
        assert permission["id"] == str(db_objs[idx].id)
        assert permission["name"] == db_objs[idx].name


def test_update_role_has_permission(db: Session) -> None:
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

    test_permission = crud.rbac.create_permissions(db, permissions=["test"])[0]

    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/role-has-permission/{role.id}",
        json={
            "old_permission_id": str(db_objs[0].id),
            "new_permission_id": str(test_permission.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 200
    assert "role_id" in res
    assert "permission_id" in res
    assert res["role_id"] == str(role.id)
    assert res["permission_id"] == str(test_permission.id)


def test_update_role_has_permission_invalid_role_id(db: Session) -> None:
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

    test_permission = crud.rbac.create_permissions(db, permissions=["test"])[0]

    uuid = uuid4()
    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/role-has-permission/{uuid}",
        json={
            "old_permission_id": str(db_objs[0].id),
            "new_permission_id": str(test_permission.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role not found"
    assert res["error"] == f"no role id: {uuid}"


def test_update_role_has_permission_invalid_permission_id(db: Session) -> None:
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
        f"/api/v1/rbac/role-has-permission/{role.id}",
        json={
            "old_permission_id": str(db_objs[0].id),
            "new_permission_id": str(uuid),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "permission not found"
    assert res["error"] == f"no permission id: {uuid}"


def test_update_not_found_role_has_permission(db: Session) -> None:
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

    test_permission = crud.rbac.create_permissions(db, permissions=["test"])[0]

    uuid = uuid4()
    header = {"authorization": f"Bearer {token}"}
    r = client.patch(
        f"/api/v1/rbac/role-has-permission/{role.id}",
        json={
            "old_permission_id": str(uuid),
            "new_permission_id": str(test_permission.id),
        },
        headers=header,
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role has permission not found"
    assert res["error"] == f"no role id: {role.id}, permission id: {uuid}"


def test_delete_not_found_role_has_permission(db: Session) -> None:
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
    r = client.delete(
        f"/api/v1/rbac/role-has-permission/{uuid}/{db_objs[0].id}", headers=header
    )
    res = r.json()
    assert r.status_code == 404
    assert "message" in res
    assert "error" in res
    assert res["message"] == "role has permission not found"
    assert res["error"] == f"no role id: {uuid}, permission id: {db_objs[0].id}"


def test_delete_role_has_permission(db: Session) -> None:
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
    r = client.delete(
        f"/api/v1/rbac/role-has-permission/{role.id}/{db_objs[0].id}", headers=header
    )
    assert r.status_code == 204
