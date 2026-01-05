from __future__ import annotations
from typing import Dict, Any, List
from kimaru_core.algorithms.base import BaseAlgorithm
from kimaru_core.algorithms.descriptor import AlgorithmDescriptor

class BasicCleaner(BaseAlgorithm):
    def describe(self):
        return AlgorithmDescriptor(
            algorithm_id="generic.data_cleaning.basic",
            version="1.0.0",
            inputs_schema={"type":"object","properties":{"rows":{"type":"array"}},"required":["rows"]},
            outputs_schema={"type":"object","properties":{"rows":{"type":"array"},"stats":{"type":"object"}},"required":["rows","stats"]},
        )

    def run(self, ctx, inputs: Dict[str, Any]) -> Dict[str, Any]:
        rows = inputs.get("rows", [])
        cleaned = []
        dropped = 0
        for r in rows:
            if r is None:
                dropped += 1
                continue
            if isinstance(r, dict):
                cleaned.append({k:v for k,v in r.items() if v is not None})
            else:
                cleaned.append(r)
        return {"rows": cleaned, "stats": {"dropped": dropped, "kept": len(cleaned)}}
