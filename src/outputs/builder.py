from typing import Dict, Any
from src.outputs.uml import generate_sequence_diagram, generate_component_diagram

def build_outputs(structured_output: Dict[str, Any]) -> Dict[str, Any]:
    uml_artifacts = []
    for diagram in structured_output.get("uml_diagrams", []):
        if diagram.get("type") == "sequence":
            uml_artifacts.append({
                "type": "sequence",
                "mermaid": generate_sequence_diagram(diagram),
            })
        elif diagram.get("type") == "component":
            uml_artifacts.append({
                "type": "component",
                "mermaid": generate_component_diagram(diagram.get("systems", [])),
            })
    return {"uml": uml_artifacts}