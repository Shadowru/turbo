import logging
from typing import Any, Dict
from src.outputs.uml import generate_sequence_diagram, generate_component_diagram

logger = logging.getLogger(__name__)

def build_outputs(structured_output: Dict[str, Any]) -> Dict[str, Any]:
    uml_artifacts = []

    diagrams = structured_output.get("uml_diagrams") or []
    if not isinstance(diagrams, (list, tuple)):
        diagrams = [diagrams]

    for idx, diagram in enumerate(diagrams):
        if not isinstance(diagram, dict):
            logger.warning(
                "Skipping UML diagram %s: expected dict, got %s",
                idx,
                type(diagram).__name__,
            )
            continue

        diagram_type = diagram.get("type")
        existing_mermaid = diagram.get("mermaid")
        description = diagram.get("description")

        if existing_mermaid:
            uml_artifacts.append(
                {
                    "type": diagram_type,
                    "mermaid": existing_mermaid,
                    "description": description,
                }
            )
            continue

        if diagram_type == "sequence":
            uml_artifacts.append(
                {
                    "type": "sequence",
                    "mermaid": generate_sequence_diagram(diagram),
                    "description": description,
                }
            )
        elif diagram_type == "component":
            uml_artifacts.append(
                {
                    "type": "component",
                    "mermaid": generate_component_diagram(diagram.get("systems", [])),
                    "description": description,
                }
            )
        else:
            logger.info("Unknown UML diagram type '%s' — skipped", diagram_type)

    return {"uml": uml_artifacts}