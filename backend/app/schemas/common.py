from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models.entities import ConnectionKind, Role


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserRead"


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=255)
    password: str = Field(min_length=8)


class UserLogin(BaseModel):
    email: EmailStr
    password: str


class UserRead(ORMModel):
    id: str
    email: EmailStr
    full_name: str
    role: Role
    is_active: bool
    created_at: datetime


class WorkspaceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=255)


class WorkspaceRead(ORMModel):
    id: str
    name: str
    slug: str
    owner_id: str
    created_at: datetime


class ConnectionCreate(BaseModel):
    workspace_id: str
    name: str
    kind: ConnectionKind
    uri: str
    is_read_only: bool = True
    selected_assets: list[str] = []


class ConnectionRead(ORMModel):
    id: str
    workspace_id: str
    name: str
    kind: ConnectionKind
    masked_uri: str
    is_read_only: bool
    selected_assets: list[str]
    created_at: datetime


class AIQuestion(BaseModel):
    workspace_id: str
    question: str
    connection_id: str | None = None
    engine: str = "sql"
    execute: bool = True


class QueryValidationRequest(BaseModel):
    engine: str
    query: str | list[dict[str, Any]]


class QueryExecutionRequest(QueryValidationRequest):
    workspace_id: str
    connection_id: str | None = None
    async_job: bool = False


class QueryResult(BaseModel):
    log_id: str
    question: str
    engine: str
    generated_query: str | list[dict[str, Any]]
    explanation: str
    safe: bool
    rows: list[dict[str, Any]] = []
    columns: list[str] = []
    insights: dict[str, Any]
    chart: dict[str, Any]
    follow_up_questions: list[str]
    agent_trace: list[dict[str, Any]] = []
    final_confidence: float = 0
    query_confidence: dict[str, Any] = {}


class WorkspaceResourceCreate(BaseModel):
    workspace_id: str
    resource_type: str
    name: str
    payload: dict[str, Any] = {}


class NotificationCreate(BaseModel):
    workspace_id: str
    title: str
    message: str
    level: str = "info"
    payload: dict[str, Any] = {}


class ScheduledReportCreate(BaseModel):
    workspace_id: str
    name: str
    cadence: str
    report_type: str = "executive"
    delivery_channels: list[str] = []
    payload: dict[str, Any] = {}


class ExportRequest(BaseModel):
    workspace_id: str
    format: str
    source_type: str
    source_id: str | None = None
    rows: list[dict[str, Any]] = []


class KnowledgeDocumentCreate(BaseModel):
    workspace_id: str
    title: str
    document_type: str
    content: str
    source_uri: str | None = None
    tags: list[str] = []


class KnowledgeSearchRequest(BaseModel):
    workspace_id: str
    query: str
    document_types: list[str] = []
    limit: int = 5


class SemanticMetricCreate(BaseModel):
    workspace_id: str
    name: str
    definition: str
    formula: str
    owner: str | None = None
    dimensions: list[str] = []
    tags: list[str] = []


class CommentCreate(BaseModel):
    workspace_id: str
    target_type: str
    target_id: str
    body: str
    mentions: list[str] = []


class ApprovalCreate(BaseModel):
    workspace_id: str
    target_type: str
    target_id: str
    action: str
    requested_reason: str = ""


class ActivityCreate(BaseModel):
    workspace_id: str
    action: str
    entity_type: str
    entity_id: str | None = None
    payload: dict[str, Any] = {}


class DashboardCreate(BaseModel):
    workspace_id: str
    name: str
    widgets: list[dict[str, Any]] = []
    shared_with: list[str] = []


class ReportCreate(BaseModel):
    workspace_id: str
    title: str
    report_type: str
    dashboard_id: str | None = None
    sections: list[dict[str, Any]] = []


class DocumentRead(BaseModel):
    id: str
    workspace_id: str
    name: str | None = None
    title: str | None = None
    payload: dict[str, Any]
    created_at: datetime


class AuditRead(ORMModel):
    id: str
    workspace_id: str | None
    actor_id: str | None
    action: str
    entity_type: str
    entity_id: str | None
    metadata_json: dict[str, Any]
    created_at: datetime
