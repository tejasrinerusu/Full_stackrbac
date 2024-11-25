from uuid import UUID

from sqlalchemy.orm import Session

from models.rbac import Permission, Role, RoleHasPermission, User, UserHasRole
from schemas.rbac import UserCreate
from utils.security import get_password_hash, verify_password


class CRUDRbac:
    def authenticate(self, db: Session, obj_in: UserCreate) -> User | None:
        user = self.get_user_by_email(db, email=obj_in.email)
        if not user:
            return None
        if not verify_password(
            password=obj_in.password, hashed_password=user.hashed_password
        ):
            return None
        return user

    # User
    def get_user_by_email(self, db: Session, email: str) -> User | None:
        return db.query(User).filter(User.email == email).first()

    def create_user(self, db: Session, obj_in: UserCreate) -> User:
        db_obj = User(
            email=obj_in.email, hashed_password=get_password_hash(obj_in.password)
        )
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_users(self, db: Session) -> list[User]:
        return db.query(User).all()

    def get_user_by_id(self, db: Session, user_id: UUID) -> User | None:
        return db.query(User).filter(User.id == user_id).first()

    def update_user(self, db: Session, user: User, new_email: str) -> User:
        user.email = new_email
        db.commit()
        db.refresh(user)
        return user

    def delete_user(self, db: Session, user: User) -> None:
        user_has_roles = self.get_all_user_has_role_by_user_id(db, user_id=user.id)
        for user_has_role in user_has_roles:
            self.delete_user_has_role(db, user_has_role)
        db.delete(user)
        db.commit()

    # Role
    def get_role_by_name(self, db: Session, name: str) -> Role:
        return db.query(Role).filter(Role.name == name).first()

    def create_role(self, db: Session, role_name: str) -> Role:
        db_obj = Role(name=role_name)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def get_roles(self, db: Session) -> list[Role]:
        return db.query(Role).all()

    def get_role_by_id(self, db: Session, role_id: UUID) -> Role | None:
        return db.query(Role).filter(Role.id == role_id).first()

    def update_role(self, db: Session, role: Role, new_role_name: str) -> Role:
        role.name = new_role_name
        db.commit()
        db.refresh(role)
        return role

    def delete_role(self, db: Session, role: Role) -> None:
        user_has_roles = self.get_all_user_has_role_by_role_id(db, role_id=role.id)
        for user_has_role in user_has_roles:
            self.delete_user_has_role(db, user_has_role)

        role_has_permissions = self.get_all_role_has_permission_by_role_id(
            db, role_id=role.id
        )
        for role_has_permission in role_has_permissions:
            self.delete_role_has_permission(db, role_has_permission)

        db.delete(role)
        db.commit()

    # RoleHasPermission
    def get_all_role_has_permission_by_role_id(
        self, db: Session, role_id: UUID
    ) -> list[RoleHasPermission]:
        return (
            db.query(RoleHasPermission)
            .filter(RoleHasPermission.role_id == role_id)
            .all()
        )

    def get_all_by_permission_id(
        self, db: Session, permission_id: UUID
    ) -> list[RoleHasPermission]:
        return (
            db.query(RoleHasPermission)
            .filter(RoleHasPermission.permission_id == permission_id)
            .all()
        )

    def get_all_permission_ids_by_role_id(
        self, db: Session, role_id: UUID
    ) -> list[UUID]:
        permission_ids = (
            db.query(RoleHasPermission.permission_id)
            .filter(RoleHasPermission.role_id == role_id)
            .all()
        )
        return [permission_id[0] for permission_id in permission_ids]

    def get_role_has_permission_by_role_id_and_permission_id(
        self, db: Session, role_id: UUID, permission_id: UUID
    ) -> RoleHasPermission | None:
        return (
            db.query(RoleHasPermission)
            .filter(RoleHasPermission.role_id == role_id)
            .filter(RoleHasPermission.permission_id == permission_id)
            .first()
        )

    def create_role_has_permission(
        self, db: Session, role_id: UUID, permission_ids: list[UUID]
    ) -> list[RoleHasPermission]:
        db_objs = [
            RoleHasPermission(role_id=role_id, permission_id=permission_id)
            for permission_id in permission_ids
        ]
        db.add_all(db_objs)
        db.commit()
        return db_objs

    def update_role_has_permission(
        self, db: Session, role_has_permission: RoleHasPermission, new_permission: UUID
    ) -> RoleHasPermission:
        role_has_permission.permission_id = new_permission
        db.commit()
        db.refresh(role_has_permission)
        return role_has_permission

    def delete_role_has_permission(
        self, db: Session, role_has_permission: RoleHasPermission
    ) -> None:
        db.delete(role_has_permission)
        db.commit()

    # UserHasRole
    def get_all_role_ids_by_user_id(self, db: Session, user_id: UUID) -> list[UUID]:
        role_ids = (
            db.query(UserHasRole.role_id).filter(UserHasRole.user_id == user_id).all()
        )
        return [role_id[0] for role_id in role_ids]

    def get_all_user_has_role_by_user_id(
        self, db: Session, user_id: UUID
    ) -> list[UserHasRole]:
        return db.query(UserHasRole).filter(UserHasRole.user_id == user_id).all()

    def get_all_user_has_role_by_role_id(
        self, db: Session, role_id: UUID
    ) -> list[UserHasRole]:
        return db.query(UserHasRole).filter(UserHasRole.role_id == role_id).all()

    def get_user_has_role_by_user_id_and_role_id(
        self, db: Session, user_id: UUID, role_id: UUID
    ) -> UserHasRole | None:
        return (
            db.query(UserHasRole)
            .filter(UserHasRole.user_id == user_id)
            .filter(UserHasRole.role_id == role_id)
            .first()
        )

    def create_user_has_role(
        self, db: Session, user_id: UUID, role_id: UUID
    ) -> UserHasRole:
        db_obj = UserHasRole(user_id=user_id, role_id=role_id)
        db.add(db_obj)
        db.commit()
        db.refresh(db_obj)
        return db_obj

    def update_user_has_role(
        self, db: Session, user_has_role: UserHasRole, new_role: UUID
    ) -> UserHasRole:
        user_has_role.role_id = new_role
        db.commit()
        db.refresh(user_has_role)
        return user_has_role

    def delete_user_has_role(self, db: Session, user_has_role: UserHasRole) -> None:
        db.delete(user_has_role)
        db.commit()

    # Permission
    def get_permission_name_by_id(self, db: Session, permission_id: UUID) -> str:
        return (
            db.query(Permission.name).filter(Permission.id == permission_id).first()[0]
        )

    def get_permission_by_id(
        self, db: Session, permission_id: UUID
    ) -> Permission | None:
        return db.query(Permission).filter(Permission.id == permission_id).first()

    def get_permission_by_name(self, db: Session, name: str) -> Permission | None:
        return db.query(Permission).filter(Permission.name == name).first()

    def get_permissions(self, db: Session) -> list[Permission]:
        return db.query(Permission).all()

    def create_permissions(
        self, db: Session, permissions: list[str]
    ) -> list[Permission]:
        db_objs = [Permission(name=permission) for permission in permissions]
        db.add_all(db_objs)
        db.commit()
        for db_obj in db_objs:
            db.refresh(db_obj)
        return db_objs

    def update_permission(
        self, db: Session, permission: Permission, new_permission_name: str
    ) -> Permission:
        permission.name = new_permission_name
        db.commit()
        db.refresh(permission)
        return permission

    def delete_permission(self, db: Session, permission: Permission) -> None:
        role_has_permissions = self.get_all_by_permission_id(
            db, permission_id=permission.id
        )
        for role_has_permission in role_has_permissions:
            self.delete_role_has_permission(db, role_has_permission)
        db.delete(permission)
        db.commit()


rbac = CRUDRbac()
