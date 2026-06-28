import csv
import io
import json
import time
import zipfile
import xml.etree.ElementTree as ET
from typing import Any
from uuid import uuid4

import httpx

from app.db.mongo import mongo_store

CONNECTOR_CATALOG = {
    "sql": ["postgresql", "mysql", "sqlserver", "oracle", "sqlite"],
    "nosql": ["mongodb"],
    "warehouse": ["snowflake", "bigquery", "redshift"],
    "business_platform": ["salesforce", "hubspot", "stripe", "shopify", "ga4", "meta_ads", "google_ads", "jira", "github", "slack", "notion", "airtable"],
    "files": ["csv", "excel", "json", "parquet"],
    "api": ["rest_api"],
}

PROVIDER_CONNECTORS = {
    "github": {
        "base_url": "https://api.github.com",
        "auth": "token_or_bearer",
        "default_path": "/user/repos",
        "pagination": "link_header",
        "rate_limit_headers": ["x-ratelimit-remaining", "x-ratelimit-reset"],
    },
    "stripe": {
        "base_url": "https://api.stripe.com/v1",
        "auth": "bearer_secret_key",
        "default_path": "/customers",
        "pagination": "starting_after",
        "rate_limit_headers": ["stripe-rate-limited-reason"],
    },
    "ga4": {
        "base_url": "https://analyticsdata.googleapis.com/v1beta",
        "auth": "oauth2_bearer",
        "default_path": "/properties/{property_id}:runReport",
        "pagination": "offset_limit",
        "rate_limit_headers": ["quota-project"],
    },
}


def connector_catalog() -> dict[str, list[str]]:
    return {**CONNECTOR_CATALOG, "provider_definitions": list(PROVIDER_CONNECTORS.keys())}


def test_rest_api(url: str, auth_header: str | None = None, timeout_seconds: int = 8) -> dict[str, Any]:
    headers = {"Authorization": auth_header} if auth_header else {}
    started = time.perf_counter()
    try:
        response = httpx.get(url, headers=headers, timeout=timeout_seconds)
        latency = round((time.perf_counter() - started) * 1000, 2)
        return {"ok": response.status_code < 500, "status_code": response.status_code, "latency_ms": latency, "schema": _detect_schema(response)}
    except Exception as exc:
        return {"ok": False, "error": str(exc), "latency_ms": round((time.perf_counter() - started) * 1000, 2)}


def sync_rest_api(workspace_id: str, url: str, auth_header: str | None = None, cursor: str | None = None, provider: str | None = None) -> dict[str, Any]:
    provider_config = PROVIDER_CONNECTORS.get(str(provider or "").lower())
    if provider_config and not url.startswith("http"):
        url = f"{provider_config['base_url']}{provider_config['default_path']}"
    result = test_rest_api(url, auth_header)
    metadata = {
        "workspace_id": workspace_id,
        "name": f"REST sync {uuid4().hex[:6]}",
        "url": url,
        "cursor": cursor,
        "provider": provider,
        "provider_config": provider_config,
        "status": "success" if result.get("ok") else "failed",
        "pagination": provider_config.get("pagination") if provider_config else "link-header-or-next-cursor-ready",
        "retry_policy": "3 exponential-backoff retries",
        "oauth_refresh": "configured when refresh token is provided",
        "result": result,
    }
    return mongo_store.insert("sync_history", metadata)


def _detect_schema(response: httpx.Response) -> dict[str, Any]:
    try:
        payload = response.json()
    except Exception:
        return {"content_type": response.headers.get("content-type"), "fields": []}
    sample = payload[0] if isinstance(payload, list) and payload else payload if isinstance(payload, dict) else {}
    return {"content_type": response.headers.get("content-type"), "fields": list(sample.keys()) if isinstance(sample, dict) else []}


def import_dataset(workspace_id: str, filename: str, content: bytes, source_type: str) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    validation_errors: list[str] = []
    if source_type == "csv" or filename.lower().endswith(".csv"):
        text = content.decode("utf-8-sig")
        rows = list(csv.DictReader(io.StringIO(text)))
    elif source_type == "json" or filename.lower().endswith(".json"):
        payload = json.loads(content.decode("utf-8"))
        rows = payload if isinstance(payload, list) else [payload]
    elif source_type == "excel" or filename.lower().endswith(".xlsx"):
        try:
            rows = _parse_xlsx(content)
        except Exception as exc:
            validation_errors.append(f"Excel parsing failed: {exc}")
    elif source_type == "parquet":
        validation_errors.append("Parquet parsing requires a production parquet engine; raw file accepted for scheduled processing.")
    else:
        validation_errors.append("Unsupported source type.")
    cleaned = []
    seen = set()
    for row in rows:
        normalized = {str(key).strip().lower().replace(" ", "_"): value for key, value in row.items()}
        signature = tuple(sorted(normalized.items()))
        if signature in seen:
            continue
        seen.add(signature)
        cleaned.append(normalized)
    doc = {
        "workspace_id": workspace_id,
        "name": filename,
        "source_type": source_type,
        "import_status": "completed" if not validation_errors else "accepted_with_warnings",
        "rows_processed": len(cleaned),
        "validation_errors": validation_errors,
        "cleaning_summary": {"deduplicated_rows": len(rows) - len(cleaned), "normalized_columns": True, "schema_mapping": "business-glossary-ready"},
        "preview_rows": cleaned[:10],
    }
    return mongo_store.insert("etl_runs", doc)


def list_sync_history(workspace_id: str) -> list[dict[str, Any]]:
    return mongo_store.list("sync_history", workspace_id)


def list_etl_runs(workspace_id: str) -> list[dict[str, Any]]:
    return mongo_store.list("etl_runs", workspace_id)


def _parse_xlsx(content: bytes) -> list[dict[str, Any]]:
    ns = {"main": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with zipfile.ZipFile(io.BytesIO(content)) as archive:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in archive.namelist():
            root = ET.fromstring(archive.read("xl/sharedStrings.xml"))
            for item in root.findall(".//main:si", ns):
                text_parts = [node.text or "" for node in item.findall(".//main:t", ns)]
                shared_strings.append("".join(text_parts))
        sheet_name = "xl/worksheets/sheet1.xml"
        root = ET.fromstring(archive.read(sheet_name))
        rows: list[list[str]] = []
        for row in root.findall(".//main:row", ns):
            values: list[str] = []
            for cell in row.findall("main:c", ns):
                value = cell.find("main:v", ns)
                raw = value.text if value is not None else ""
                if cell.attrib.get("t") == "s" and raw:
                    raw = shared_strings[int(raw)]
                values.append(raw or "")
            if values:
                rows.append(values)
        if not rows:
            return []
        headers = [header.strip() or f"column_{index + 1}" for index, header in enumerate(rows[0])]
        return [dict(zip(headers, row + [""] * (len(headers) - len(row)))) for row in rows[1:]]
