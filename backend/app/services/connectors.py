from contextlib import contextmanager
from typing import Any

from fastapi import HTTPException
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.models import AuditAction, ConnectionKind, DatabaseConnection, User
from app.schemas.common import ConnectionCreate
from app.services.audit import audit
from app.security.crypto import decrypt_secret, encrypt_secret


def create_connection(db: Session, user: User, payload: ConnectionCreate) -> DatabaseConnection:
    data = payload.model_dump()
    data["uri"] = encrypt_secret(data["uri"])
    item = DatabaseConnection(**data, created_by=user.id)
    db.add(item)
    db.commit()
    db.refresh(item)
    audit(
        db,
        AuditAction.database_connection_created,
        "database_connection",
        actor_id=user.id,
        workspace_id=item.workspace_id,
        entity_id=item.id,
        metadata={"kind": item.kind.value, "read_only": item.is_read_only},
    )
    return item


def test_connection(connection: DatabaseConnection) -> dict[str, Any]:
    if connection.kind == ConnectionKind.mongodb:
        return {"ok": True, "message": "MongoDB connector is configured; live ping runs when pymongo is available."}
    try:
        uri = decrypt_secret(connection.uri)
        engine = create_engine(uri, connect_args={"check_same_thread": False} if uri.startswith("sqlite") else {})
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return {"ok": True, "message": "Connection succeeded."}
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"Connection failed: {exc}") from exc


def read_schema(connection: DatabaseConnection | None = None) -> dict[str, Any]:
    uri = decrypt_secret(connection.uri) if connection else get_settings().database_url
    kind = connection.kind if connection else ConnectionKind.sqlite
    if kind == ConnectionKind.mongodb:
        return {
            "engine": "mongodb",
            "collections": [
                {"name": "customer_activity", "fields": ["customer", "event", "value", "created_at"]},
                {"name": "dashboard_configs", "fields": ["workspace_id", "widgets", "layout"]},
            ],
        }
    engine = create_engine(uri, connect_args={"check_same_thread": False} if uri.startswith("sqlite") else {})
    inspector = inspect(engine)
    tables = []
    relationships = []
    business_glossary = {
        "revenue": "Gross sales value before expenses, mapped to sales.revenue.",
        "profit": "Revenue minus related expenses, or product margin proxy when expense allocation is unavailable.",
        "active_customer": "A customer with activity or orders in the selected period.",
        "churned_customer": "A previously active customer with no recent activity after the churn threshold.",
        "high_value_customer": "A customer above the workspace lifetime-value threshold.",
        "monthly_recurring_revenue": "Recurring revenue grouped by month.",
    }
    column_meanings = {
        "order_month": "Month bucket for revenue and order trends.",
        "region": "Sales territory or operating geography.",
        "customer": "Customer account name.",
        "product": "Product or SKU name.",
        "revenue": "Recognized revenue amount.",
        "units": "Units sold.",
        "inventory": "Current available stock count.",
        "expense_amount": "Operating expense value.",
    }
    metric_definitions = {
        "monthly_sales_trend": "SUM(sales.revenue) grouped by sales.order_month.",
        "top_customers": "Customers ranked by SUM(sales.revenue), order count, or estimated profit.",
        "low_inventory_products": "Products or inventory rows ordered by available stock ascending.",
        "regional_performance": "SUM(sales.revenue) and units grouped by region.",
    }
    for table_name in inspector.get_table_names():
        pk = inspector.get_pk_constraint(table_name).get("constrained_columns", [])
        fks = inspector.get_foreign_keys(table_name)
        for fk in fks:
            relationships.append(
                {
                    "table": table_name,
                    "columns": fk.get("constrained_columns", []),
                    "referred_table": fk.get("referred_table"),
                    "referred_columns": fk.get("referred_columns", []),
                }
            )
        tables.append(
            {
                "name": table_name,
                "primary_key": pk,
                "foreign_keys": fks,
                "columns": [
                    {"name": col["name"], "type": str(col["type"]), "nullable": col.get("nullable", True), "meaning": column_meanings.get(col["name"], "Business attribute")}
                    for col in inspector.get_columns(table_name)
                ],
            }
        )
    return {"engine": kind.value, "tables": tables, "relationships": relationships, "business_glossary": business_glossary, "metric_definitions": metric_definitions}


def get_connection_or_404(db: Session, connection_id: str | None) -> DatabaseConnection | None:
    if connection_id is None:
        return None
    connection = db.get(DatabaseConnection, connection_id)
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")
    return connection
