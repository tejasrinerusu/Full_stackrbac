import uuid

from sqlalchemy import Column, ForeignKey, String
from sqlalchemy.dialects.postgresql import UUID

from db.session import Base


class User(Base):
    __tablename__ = "user"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String, unique=True, nullable=False)
    hashed_password = Column(String, nullable=False)


class UserHasRole(Base):
    __tablename__ = "user_has_role"

    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, nullable=False
    )
    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id"), primary_key=True, nullable=False
    )


class Role(Base):
    __tablename__ = "role"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class RoleHasPermission(Base):
    __tablename__ = "role_has_permission"

    role_id = Column(
        UUID(as_uuid=True), ForeignKey("role.id"), primary_key=True, nullable=False
    )
    permission_id = Column(
        UUID(as_uuid=True),
        ForeignKey("permission.id"),
        primary_key=True,
        nullable=False,
    )


class Permission(Base):
    __tablename__ = "permission"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class Group(Base):
    __tablename__ = "group"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)


class GroupHasUser(Base):
    __tablename__ = "group_has_user"

    group_id = Column(
        UUID(as_uuid=True), ForeignKey("group.id"), primary_key=True, nullable=False
    )
    user_id = Column(
        UUID(as_uuid=True), ForeignKey("user.id"), primary_key=True, nullable=False
    )
