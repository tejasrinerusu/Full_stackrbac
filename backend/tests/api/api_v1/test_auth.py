from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from api.deps import get_db
import crud
from main import app
from schemas.rbac import UserCreate
from tests.conftest import override_get_db

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)


def test_login_success(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    admin = UserCreate(email=email, password=password)
    db_obj = crud.rbac.create_user(db, obj_in=admin)
    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    assert r.status_code == 201
    assert "permissions" in res
    assert "token" in res
    assert res["token"]


def test_login_wrong_password(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    admin = UserCreate(email=email, password=password)
    db_obj = crud.rbac.create_user(db, obj_in=admin)
    login_data = {"email": email, "password": "87654321"}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    assert r.status_code == 400
    assert "message" in res
    assert res["message"] == "Incorrect email or password"


def test_login_invalid_user(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    admin = UserCreate(email=email, password=password)
    db_obj = crud.rbac.create_user(db, obj_in=admin)
    login_data = {"email": "invalid@test.com", "password": "87654321"}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()
    assert r.status_code == 400
    assert "message" in res
    assert res["message"] == "Incorrect email or password"


def test_auth_success_without_permissions(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    admin = UserCreate(email=email, password=password)
    db_obj = crud.rbac.create_user(db, obj_in=admin)
    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    auth_data = {"permissions": [], "token": res["token"]}
    r = client.post("/api/v1/auth", json=auth_data)
    res = r.json()
    assert r.status_code == 201
    assert "message" in res
    assert res["message"] == "success"


def test_auth_success_with_permissions(db: Session) -> None:
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

    auth_data = {
        "permissions": [
            "setting.create",
            "setting.read",
            "setting.update",
            "setting.delete",
        ],
        "token": res["token"],
    }
    r = client.post("/api/v1/auth", json=auth_data)
    res = r.json()
    assert r.status_code == 201
    assert "message" in res
    assert res["message"] == "success"


def test_auth_without_permission(db: Session) -> None:
    email = "admin@test.com"
    password = "12345678"
    permissions = ["setting.create", "setting.read", "setting.update", "setting.delete"]
    admin = UserCreate(email=email, password=password)
    user = crud.rbac.create_user(db, obj_in=admin)

    role = crud.rbac.create_role(db, role_name="admin")

    crud.rbac.create_user_has_role(db, user_id=user.id, role_id=role.id)

    db_objs = crud.rbac.create_permissions(db, permissions=permissions)

    login_data = {"email": email, "password": password}
    r = client.post("/api/v1/auth/login", json=login_data)
    res = r.json()

    auth_data = {
        "permissions": [
            "invalid.create",
        ],
        "token": res["token"],
    }
    r = client.post("/api/v1/auth", json=auth_data)
    res = r.json()
    assert r.status_code == 401
    assert "message" in res
    assert res["message"] == "user does not have permission"


def test_auth_invalid_jwt() -> None:
    auth_data = {
        "permissions": [],
        "token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJmdWxsLXN0YWNrLXJiYWMiLCJleHAiOjE2zc0MjY5MzksImlhdCI6MTY3NzMxMTczOSwicGVybWlzc2lvbnMiOlsiYTE0MTczOTItYmJkOS00ZGJlLWFiMDktMGFlNzEyYTE1NzgwIiwiMjhhNzcwYTUtMDFhMC00YzkzLWFkOTQtZWFhNmJhYjliMzhlIiwiYWNhOTBhZmYtMTM1MS00MTU0LWFmMTYtYWM1ZmNjOGY2MDkwIiwiMDJjMzE5ZmEtN2E5Yi00MDg0LWE0N2QtNWI3MGRkOGYzMzhkIl0sImVtYWlsIjoiYWRtaW5AdGVzdC5jb20ifQ.yXqQ7BrN8TNSxieqa-caeXvVnXkWOKKeUmhralfcqt0",
    }
    r = client.post("/api/v1/auth", json=auth_data)
    res = r.json()
    assert r.status_code == 401
    assert "message" in res
    assert res["message"] == "user is not authorized"
