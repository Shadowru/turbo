from dataclasses import dataclass
from typing import Dict, Any
import json
from src.core.orchestrator import run_bft_analysis
from src.outputs.builder import build_outputs

@dataclass
class PipelineResult:
    raw_llm_output: str
    structured_output: Dict[str, Any]
    artifacts: Dict[str, Any]

def process_bft(bft_id: str, text: str) -> PipelineResult:
    orchestrator_result = run_bft_analysis(bft_id, text)
    raw_json = orchestrator_result["llm_result"]
    structured_output = json.loads(raw_json)

    artifacts = build_outputs(structured_output)
    return PipelineResult(
        raw_llm_output=raw_json,
        structured_output=structured_output,
        artifacts=artifacts,
    )