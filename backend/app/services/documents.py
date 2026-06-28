import csv
import io
import json
import zipfile
from datetime import datetime
from typing import Any

from app.db.mongo import mongo_store


def create_dashboard(payload: dict) -> dict:
    return mongo_store.insert("dashboards", {"payload": payload, **payload})


def list_dashboards(workspace_id: str) -> list[dict]:
    return mongo_store.list("dashboards", workspace_id)


def get_dashboard(document_id: str) -> dict | None:
    return mongo_store.get("dashboards", document_id)


def update_dashboard(document_id: str, patch: dict) -> dict | None:
    return mongo_store.update("dashboards", document_id, patch)


def delete_dashboard(document_id: str) -> bool:
    return mongo_store.delete("dashboards", document_id)


def duplicate_dashboard(document_id: str) -> dict | None:
    original = get_dashboard(document_id)
    if not original:
        return None
    clone = {k: v for k, v in original.items() if k not in {"id", "created_at", "updated_at"}}
    clone["name"] = f"{clone.get('name', 'Dashboard')} Copy"
    return create_dashboard(clone)


def create_report(payload: dict) -> dict:
    defaults = {
        "kpis": [{"label": "Revenue", "value": "$1.38M"}, {"label": "Growth", "value": "+14.2%"}, {"label": "At-risk accounts", "value": "3"}],
        "ai_explanation": "Executive summary generated from the selected dashboard and recent query logs.",
        "export": {"pdf": "downloadable", "excel": "downloadable", "csv": "downloadable", "powerpoint": "downloadable"},
        "version": 1,
    }
    return mongo_store.insert("reports", {"payload": {**defaults, **payload}, **payload})


def list_reports(workspace_id: str) -> list[dict]:
    return mongo_store.list("reports", workspace_id)


def get_report(document_id: str) -> dict | None:
    return mongo_store.get("reports", document_id)


def update_report(document_id: str, patch: dict) -> dict | None:
    existing = get_report(document_id) or {}
    version = int(existing.get("payload", {}).get("version") or existing.get("version") or 1) + 1
    patch = {**patch, "version": version}
    if "payload" in existing:
        patch["payload"] = {**existing.get("payload", {}), **patch}
    return mongo_store.update("reports", document_id, patch)


def _rows_from_document(document: dict[str, Any] | None) -> list[dict[str, Any]]:
    if not document:
        return []
    widgets = document.get("widgets") or document.get("payload", {}).get("widgets", [])
    rows: list[dict[str, Any]] = []
    for widget in widgets:
        rows.extend(widget.get("rows", []) if isinstance(widget, dict) else [])
    if rows:
        return rows
    kpis = document.get("payload", {}).get("kpis", document.get("kpis", []))
    return [{"label": item.get("label"), "value": item.get("value")} for item in kpis if isinstance(item, dict)]


def csv_bytes(rows: list[dict[str, Any]]) -> bytes:
    output = io.StringIO()
    if not rows:
        rows = [{"status": "empty"}]
    writer = csv.DictWriter(output, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)
    return output.getvalue().encode("utf-8")


def excel_bytes(rows: list[dict[str, Any]]) -> bytes:
    csv_payload = csv_bytes(rows).decode("utf-8")
    html = f"<html><body><table><pre>{csv_payload}</pre></table></body></html>"
    return html.encode("utf-8")


def pdf_bytes(title: str, rows: list[dict[str, Any]]) -> bytes:
    text = json.dumps({"title": title, "generated_at": datetime.utcnow().isoformat(), "rows": rows[:20]}, default=str)
    stream = f"BT /F1 10 Tf 40 760 Td ({text[:900].replace('(', '[').replace(')', ']')}) Tj ET"
    pdf = f"%PDF-1.4\n1 0 obj << /Type /Catalog /Pages 2 0 R >> endobj\n2 0 obj << /Type /Pages /Kids [3 0 R] /Count 1 >> endobj\n3 0 obj << /Type /Page /Parent 2 0 R /Resources << /Font << /F1 4 0 R >> >> /MediaBox [0 0 612 792] /Contents 5 0 R >> endobj\n4 0 obj << /Type /Font /Subtype /Type1 /BaseFont /Helvetica >> endobj\n5 0 obj << /Length {len(stream)} >> stream\n{stream}\nendstream endobj\ntrailer << /Root 1 0 R >>\n%%EOF"
    return pdf.encode("utf-8")


def pptx_bytes(title: str, rows: list[dict[str, Any]]) -> bytes:
    buffer = io.BytesIO()
    summary = json.dumps({"title": title, "rows": rows[:10]}, default=str)
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", "<?xml version='1.0'?><Types xmlns='http://schemas.openxmlformats.org/package/2006/content-types'><Default Extension='xml' ContentType='application/xml'/></Types>")
        archive.writestr("ppt/presentation.xml", f"<presentation><slide>{summary}</slide></presentation>")
    return buffer.getvalue()


def export_document(document: dict[str, Any] | None, export_format: str) -> tuple[bytes, str, str]:
    title = str((document or {}).get("title") or (document or {}).get("name") or "InsightAI Export")
    rows = _rows_from_document(document)
    if export_format == "csv":
        return csv_bytes(rows), "text/csv", "export.csv"
    if export_format == "excel":
        return excel_bytes(rows), "application/vnd.ms-excel", "export.xls"
    if export_format == "pdf":
        return pdf_bytes(title, rows), "application/pdf", "export.pdf"
    if export_format == "powerpoint":
        return pptx_bytes(title, rows), "application/vnd.openxmlformats-officedocument.presentationml.presentation", "export.pptx"
    return json.dumps(document or {}).encode("utf-8"), "application/json", "export.json"
