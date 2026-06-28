import json
import re
from typing import Any

MUTATING_SQL = re.compile(r"\b(drop|delete|update|insert|alter|truncate|create|merge|grant|revoke|replace|vacuum)\b", re.I)
READ_SQL = re.compile(r"^\s*(with\b[\s\S]+?select\b|select\b)", re.I)
MONGO_WRITE_STAGES = {"$out", "$merge", "$set", "$unset", "$addFields", "$projectWrite"}


class QuerySafetyError(ValueError):
    pass


def normalize_sql(query: str) -> str:
    return query.strip().rstrip(";")


def ensure_sql_is_safe(query: str, default_limit: int = 100) -> str:
    normalized = normalize_sql(query)
    if not READ_SQL.match(normalized):
        raise QuerySafetyError("Only SELECT statements are allowed.")
    if MUTATING_SQL.search(normalized):
        raise QuerySafetyError("Mutating SQL keywords are blocked.")
    if ";" in normalized:
        raise QuerySafetyError("Multiple SQL statements are not allowed.")
    if not re.search(r"\blimit\s+\d+\b", normalized, re.I):
        normalized = f"{normalized} LIMIT {default_limit}"
    return normalized


def ensure_mongo_pipeline_is_safe(pipeline: list[dict[str, Any]] | str) -> list[dict[str, Any]]:
    if isinstance(pipeline, str):
        try:
            pipeline = json.loads(pipeline)
        except json.JSONDecodeError as exc:
            raise QuerySafetyError("MongoDB pipeline must be valid JSON.") from exc
    if not isinstance(pipeline, list):
        raise QuerySafetyError("MongoDB aggregation pipeline must be a list.")
    for stage in pipeline:
        if not isinstance(stage, dict) or len(stage) != 1:
            raise QuerySafetyError("Each MongoDB pipeline stage must be a single-key object.")
        operator = next(iter(stage))
        if operator in MONGO_WRITE_STAGES:
            raise QuerySafetyError(f"MongoDB write stage {operator} is blocked.")
    if not any("$limit" in stage for stage in pipeline):
        pipeline.append({"$limit": 100})
    return pipeline


def validate_query(engine: str, query: str | list[dict[str, Any]]) -> tuple[bool, str | list[dict[str, Any]], str | None]:
    try:
        if engine == "mongodb":
            return True, ensure_mongo_pipeline_is_safe(query), None
        return True, ensure_sql_is_safe(str(query)), None
    except QuerySafetyError as exc:
        return False, query, str(exc)
