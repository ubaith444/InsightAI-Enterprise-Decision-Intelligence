from copy import deepcopy
from datetime import datetime
from typing import Any
from uuid import uuid4

from app.core.config import get_settings


class MongoDocumentStore:
    def __init__(self) -> None:
        self.settings = get_settings()
        self._memory: dict[str, list[dict[str, Any]]] = {
            "dashboards": [],
            "reports": [],
            "chat_history": [],
            "user_preferences": [],
            "ai_memory": [],
            "report_templates": [],
            "business_glossary": [],
            "saved_prompts": [],
            "notifications": [],
            "scheduled_reports": [],
            "exports": [],
            "api_keys": [],
            "billing": [],
            "team_management": [],
            "workspace_settings": [],
            "profile_settings": [],
            "knowledge_documents": [],
            "knowledge_searches": [],
            "sync_history": [],
            "etl_runs": [],
            "semantic_metrics": [],
            "data_lineage": [],
            "comments": [],
            "activity_feed": [],
            "approvals": [],
            "dashboard_versions": [],
            "report_versions": [],
            "monitoring_events": [],
        }
        self._db = None
        try:
            from pymongo import MongoClient

            client = MongoClient(self.settings.mongo_url, serverSelectionTimeoutMS=400)
            client.admin.command("ping")
            self._db = client[self.settings.mongo_database]
        except Exception:
            self._db = None

    def insert(self, collection: str, document: dict[str, Any]) -> dict[str, Any]:
        payload = deepcopy(document)
        payload.setdefault("id", str(uuid4()))
        payload.setdefault("created_at", datetime.utcnow())
        if self._db is not None:
            self._db[collection].insert_one({**payload, "_id": payload["id"]})
        else:
            self._memory.setdefault(collection, []).append(payload)
        return payload

    def list(self, collection: str, workspace_id: str | None = None) -> list[dict[str, Any]]:
        if self._db is not None:
            query = {"workspace_id": workspace_id} if workspace_id else {}
            return [{k: v for k, v in doc.items() if k != "_id"} for doc in self._db[collection].find(query)]
        items = self._memory.setdefault(collection, [])
        return [deepcopy(item) for item in items if workspace_id is None or item.get("workspace_id") == workspace_id]

    def update(self, collection: str, document_id: str, patch: dict[str, Any]) -> dict[str, Any] | None:
        patch = {**patch, "updated_at": datetime.utcnow()}
        if self._db is not None:
            self._db[collection].update_one({"_id": document_id}, {"$set": patch})
            doc = self._db[collection].find_one({"_id": document_id})
            return None if doc is None else {k: v for k, v in doc.items() if k != "_id"}
        for item in self._memory.setdefault(collection, []):
            if item.get("id") == document_id:
                item.update(patch)
                return deepcopy(item)
        return None

    def get(self, collection: str, document_id: str) -> dict[str, Any] | None:
        if self._db is not None:
            doc = self._db[collection].find_one({"_id": document_id})
            return None if doc is None else {k: v for k, v in doc.items() if k != "_id"}
        for item in self._memory.setdefault(collection, []):
            if item.get("id") == document_id:
                return deepcopy(item)
        return None

    def delete(self, collection: str, document_id: str) -> bool:
        if self._db is not None:
            result = self._db[collection].delete_one({"_id": document_id})
            return result.deleted_count > 0
        items = self._memory.setdefault(collection, [])
        before = len(items)
        self._memory[collection] = [item for item in items if item.get("id") != document_id]
        return len(self._memory[collection]) < before


mongo_store = MongoDocumentStore()
