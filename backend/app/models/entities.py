import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, JSON, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.session import Base
from app.security.crypto import mask_secret


def new_id() -> str:
    return str(uuid.uuid4())


class Role(str, enum.Enum):
    super_admin = "Super Admin"
    admin = "Admin"
    analyst = "Analyst"
    viewer = "Viewer"


class ConnectionKind(str, enum.Enum):
    postgresql = "postgresql"
    mysql = "mysql"
    sqlserver = "sqlserver"
    oracle = "oracle"
    sqlite = "sqlite"
    mongodb = "mongodb"
    snowflake = "snowflake"
    bigquery = "bigquery"
    redshift = "redshift"
    rest_api = "rest_api"
    salesforce = "salesforce"
    hubspot = "hubspot"
    stripe = "stripe"
    shopify = "shopify"
    ga4 = "ga4"
    meta_ads = "meta_ads"
    google_ads = "google_ads"
    jira = "jira"
    github = "github"
    slack = "slack"
    notion = "notion"
    airtable = "airtable"


class AuditAction(str, enum.Enum):
    login = "login"
    database_connection_created = "database_connection_created"
    query_generated = "query_generated"
    query_executed = "query_executed"
    dashboard_created = "dashboard_created"
    report_generated = "report_generated"
    user_role_changed = "user_role_changed"


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    full_name: Mapped[str] = mapped_column(String(255))
    hashed_password: Mapped[str] = mapped_column(String(255))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.analyst)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    memberships: Mapped[list["WorkspaceMember"]] = relationship(back_populates="user")


class Workspace(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(255))
    slug: Mapped[str] = mapped_column(String(255), unique=True, index=True)
    owner_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    members: Mapped[list["WorkspaceMember"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class WorkspaceMember(Base):
    __tablename__ = "workspace_members"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="uq_workspace_user"),)

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    role: Mapped[Role] = mapped_column(Enum(Role), default=Role.analyst)

    workspace: Mapped[Workspace] = relationship(back_populates="members")
    user: Mapped[User] = relationship(back_populates="memberships")


class DatabaseConnection(Base):
    __tablename__ = "database_connections"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), index=True)
    name: Mapped[str] = mapped_column(String(255))
    kind: Mapped[ConnectionKind] = mapped_column(Enum(ConnectionKind))
    uri: Mapped[str] = mapped_column(Text)
    is_read_only: Mapped[bool] = mapped_column(Boolean, default=True)
    selected_assets: Mapped[list[str]] = mapped_column(JSON, default=list)
    created_by: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    @property
    def masked_uri(self) -> str:
        return mask_secret(self.uri)


class QueryLog(Base):
    __tablename__ = "query_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"), index=True)
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    connection_id: Mapped[str | None] = mapped_column(String, ForeignKey("database_connections.id"), nullable=True)
    question: Mapped[str] = mapped_column(Text)
    generated_query: Mapped[str] = mapped_column(Text)
    engine: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(50), default="generated")
    row_count: Mapped[int] = mapped_column(Integer, default=0)
    error: Mapped[str | None] = mapped_column(Text, nullable=True)
    insights: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AIUsageLog(Base):
    __tablename__ = "ai_usage_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    workspace_id: Mapped[str] = mapped_column(String, ForeignKey("workspaces.id"))
    user_id: Mapped[str] = mapped_column(String, ForeignKey("users.id"))
    provider: Mapped[str] = mapped_column(String(100), default="mock")
    model: Mapped[str] = mapped_column(String(100), default="mock-insightai")
    prompt_tokens: Mapped[int] = mapped_column(Integer, default=0)
    completion_tokens: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=new_id)
    workspace_id: Mapped[str | None] = mapped_column(String, ForeignKey("workspaces.id"), nullable=True)
    actor_id: Mapped[str | None] = mapped_column(String, ForeignKey("users.id"), nullable=True)
    action: Mapped[AuditAction] = mapped_column(Enum(AuditAction))
    entity_type: Mapped[str] = mapped_column(String(100))
    entity_id: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict] = mapped_column(JSON, default=dict)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
