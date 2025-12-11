from __future__ import annotations

import re
from typing import Any, Dict, List


def _sanitize_identifier(raw: str | None, fallback: str) -> str:
    """Преобразует произвольное имя в безопасный идентификатор Mermaid."""
    if not raw:
        raw = fallback
    normalized = re.sub(r"\s+", "_", raw.strip())
    normalized = re.sub(r"[^0-9a-zA-Z_]", "", normalized)
    if not normalized:
        normalized = fallback
    if normalized[0].isdigit():
        normalized = f"_{normalized}"
    return normalized.lower()


def _escape_label(text: str | None) -> str:
    if text is None:
        return ""
    return (
        str(text)
        .replace('"', r"\"")
        .replace("\n", "<br/>")
        .strip()
    )


def generate_sequence_diagram(diagram_spec: Dict[str, Any]) -> str:
    lines: List[str] = ["sequenceDiagram"]
    steps = diagram_spec.get("steps") or []
    actor_order: List[str] = []
    seen: set[str] = set()

    for name in diagram_spec.get("actors") or []:
        if name and name not in seen:
            actor_order.append(name)
            seen.add(name)

    for step in steps:
        for name in (step.get("from"), step.get("to")):
            if name and name not in seen:
                actor_order.append(name)
                seen.add(name)

    alias_map: Dict[str, str] = {}
    for idx, name in enumerate(actor_order):
        alias = _sanitize_identifier(name, f"actor{idx}")
        alias_map[name] = alias
        lines.append(f'participant "{_escape_label(name)}" as {alias}')

    def ensure_participant(name: str) -> str:
        if name not in alias_map:
            alias = _sanitize_identifier(name, f"actor{len(alias_map)}")
            alias_map[name] = alias
            lines.append(f'participant "{_escape_label(name)}" as {alias}')
        return alias_map[name]

    for step in steps:
        sender = step.get("from")
        receiver = step.get("to")
        if not sender or not receiver:
            continue

        sender_alias = ensure_participant(sender)
        receiver_alias = ensure_participant(receiver)

        message = _escape_label(step.get("message", ""))
        arrow = step.get("arrow") or "->>"
        if arrow not in {"->", "-->", "->>", "-->>", "-)", "--)", "->)", "-->"}:
            arrow = "->>"
        lines.append(f"{sender_alias} {arrow} {receiver_alias}: {message}")

    return "\n".join(lines)


def generate_component_diagram(systems: List[Dict[str, Any]]) -> str:
    lines: List[str] = ["flowchart LR"]
    node_registry: Dict[str, str] = {}
    created_nodes: set[str] = set()
    style_lines: List[str] = []
    connections: set[tuple[str, str, str]] = set()
    counter = 0

    def register_alias(alias: str | None, node_id: str) -> None:
        if alias:
            node_registry.setdefault(alias.lower(), node_id)

    def ensure_node(
        name: str | None,
        label: str | None = None,
        existing: bool = True,
    ) -> str:
        nonlocal counter

        search_keys = [name, label]
        for key in search_keys:
            if key and key.lower() in node_registry:
                return node_registry[key.lower()]

        base = name or label or f"node{counter}"
        node_id = _sanitize_identifier(base, f"node{counter}")
        if node_id in created_nodes:
            node_id = f"{node_id}_{counter}"

        created_nodes.add(node_id)
        safe_label = _escape_label(label or name or base)
        lines.append(f'{node_id}["{safe_label}"]')

        for key in search_keys:
            register_alias(key, node_id)

        if not existing:
            style_lines.append(
                f"style {node_id} fill:#FFF5F5,stroke:#FF6B6B,stroke-width:2px,stroke-dasharray:5 3"
            )

        counter += 1
        return node_id

    def format_edge_label(label: str | None) -> str:
        if not label:
            return ""
        safe = _escape_label(label)
        safe = safe.replace("|", r"\|").replace("[", r"\[").replace("]", r"\]")
        return f'|"{safe}"|'

    # Основные узлы
    for idx, system in enumerate(systems or []):
        sys_name = system.get("system_id") or system.get("label") or f"system_{idx}"
        label = system.get("label") or sys_name
        existing = system.get("existing", True)
        node_id = ensure_node(sys_name, label, existing)

        register_alias(system.get("system_id"), node_id)
        register_alias(system.get("label"), node_id)
        register_alias(sys_name, node_id)

    # Связи
    for system in systems or []:
        sys_name = system.get("system_id") or system.get("label")
        source_label = system.get("label") or sys_name
        existing = system.get("existing", True)
        source_id = ensure_node(sys_name, source_label, existing)

        for integration in system.get("integrations", []):
            target_name = integration.get("target")
            if not target_name:
                continue

            target_label = integration.get("target_label") or target_name
            target_existing = integration.get("existing", True)
            target_id = ensure_node(target_name, target_label, target_existing)

            edge_label = format_edge_label(integration.get("label"))
            key = (source_id, target_id, edge_label)
            if key in connections:
                continue
            connections.add(key)

            line = f"{source_id} --> {target_id}"
            if edge_label:
                line = f"{source_id} -->{edge_label} {target_id}"
            lines.append(line)

    lines.extend(style_lines)
    return "\n".join(lines)