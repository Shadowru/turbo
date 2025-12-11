import re
from typing import Any, Dict, Iterable, List, Tuple

def unwrap_document(doc: Any) -> Tuple[Dict[str, Any], str]:
    """Возвращает (metadata, page_content) для словарей и Document-подобных объектов."""
    if doc is None:
        return {}, ""

    if isinstance(doc, dict):
        metadata = doc.get("metadata") or {}
        text = (
            doc.get("page_content")
            or doc.get("text")
            or doc.get("content")
            or ""
        )
        return metadata, text

    metadata = getattr(doc, "metadata", None) or {}
    text = (
        getattr(doc, "page_content", None)
        or getattr(doc, "text", None)
        or getattr(doc, "content", None)
        or ""
    )
    return metadata, text

def extract_known_systems(documents: Iterable[Any]) -> List[Dict[str, str]]:
    systems: Dict[str, Dict[str, str]] = {}
    pattern_id = re.compile(r"(?:system[_\s-]?id|id\s*):\s*([a-zA-Z0-9_.-]+)", re.IGNORECASE)
    pattern_name = re.compile(r"(?:system\s*name|название|title|имя)\s*[:|-]\s*(.+)", re.IGNORECASE)

    for doc in documents:
        metadata, text = unwrap_document(doc)
        system_id = metadata.get("system_id")

        if not system_id:
            match_id = pattern_id.search(text)
            if match_id:
                system_id = match_id.group(1).strip()

        if not system_id:
            continue

        system_name = metadata.get("system_name") or metadata.get("title")
        if not system_name:
            match_name = pattern_name.search(text)
            if match_name:
                system_name = match_name.group(1).strip()

        system_name = system_name or system_id
        key = system_id.lower()
        if key not in systems:
            systems[key] = {
                "system_id": system_id,
                "system_name": system_name,
            }

        alias = metadata.get("alias") or metadata.get("aliases")
        if alias:
            systems[key]["alias"] = alias

    return list(systems.values())

__all__ = ["extract_known_systems", "unwrap_document"]