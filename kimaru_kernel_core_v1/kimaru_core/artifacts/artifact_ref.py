from __future__ import annotations
from pydantic import BaseModel

class ArtifactRef(BaseModel):
    kind: str
    artifact_id: str

    def key(self) -> str:
        return f"{self.kind}:{self.artifact_id}"
