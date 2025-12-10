from typing import Dict, Any, List

def generate_sequence_diagram(diagram_spec: Dict[str, Any]) -> str:
    actors = diagram_spec.get("actors", [])
    steps = diagram_spec.get("steps", [])

    lines = ["sequenceDiagram"]
    for actor in actors:
        lines.append(f"participant {actor}")

    for step in steps:
        sender = step["from"]
        receiver = step["to"]
        message = step["message"]
        lines.append(f"{sender}->>{receiver}: {message}")

    return "\n".join(lines)

def generate_component_diagram(systems: List[Dict[str, Any]]) -> str:
    lines = ["flowchart LR"]
    for system in systems:
        system_id = system["system_id"]
        label = system.get("label", system_id)
        is_new = system.get("existing", True) is False
        decoration = "::new" if is_new else ""
        lines.append(f"{system_id}{decoration}({label})")

    for system in systems:
        for integration in system.get("integrations", []):
            target = integration["target"]
            label = integration["label"]
            lines.append(f"{system['system_id']} -->|{label}| {target}")

    return "\n".join(lines)