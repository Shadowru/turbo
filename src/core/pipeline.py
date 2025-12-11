from dataclasses import dataclass
from typing import Dict, Any
from src.utils.json_utils import extract_json_from_response, LLMJsonParseError
from src.core.orchestrator import run_bft_analysis
from src.outputs.builder import build_outputs

@dataclass
class PipelineResult:
    raw_llm_output: str
    structured_output: Dict[str, Any]
    artifacts: Dict[str, Any]
    retrieved_context: str | None
    retrieved_documents: Any

def process_bft(bft_id: str, text: str) -> PipelineResult:
    orchestrator_result = run_bft_analysis(bft_id, text)
    raw_json = orchestrator_result["llm_result"]

    try:
        structured_output = extract_json_from_response(raw_json)
    except LLMJsonParseError as exc:
        raise ValueError(f"LLM returned invalid JSON: {exc}") from exc
    artifacts = build_outputs(structured_output)
    
    return PipelineResult(
        raw_llm_output=raw_json,
        structured_output=structured_output,
        artifacts=artifacts,
        retrieved_context=orchestrator_result.get("retrieved_context"),
        retrieved_documents=orchestrator_result.get("retrieved_documents"),
    )