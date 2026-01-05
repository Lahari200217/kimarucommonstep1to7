from __future__ import annotations
import os, json
from typing import Optional, Dict, Any, List
from pathlib import Path

from kimaru_core.artifacts.artifact_ref import ArtifactRef
from kimaru_core.artifacts.artifact_models import ArtifactEnvelope
from kimaru_core.utils.hashing import canonical_json_dumps, sha256_bytes

class ArtifactStore:
    def put(self, ref: ArtifactRef, envelope: ArtifactEnvelope) -> None: ...
    def get(self, ref: ArtifactRef) -> ArtifactEnvelope: ...
    def exists(self, ref: ArtifactRef) -> bool: ...
    def list(self, kind: str, limit: int = 100) -> List[ArtifactRef]: ...

class FileSystemArtifactStore(ArtifactStore):
    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _path(self, ref: ArtifactRef) -> Path:
        d = self.base_dir / ref.kind
        d.mkdir(parents=True, exist_ok=True)
        return d / f"{ref.artifact_id}.json"

    def exists(self, ref: ArtifactRef) -> bool:
        return self._path(ref).exists()

    def put(self, ref: ArtifactRef, envelope: ArtifactEnvelope) -> None:
        p = self._path(ref)
        data = envelope.model_dump()
        raw = canonical_json_dumps(data).encode("utf-8")
        checksum = sha256_bytes(raw)
        # immutability: if exists, must match bytes
        if p.exists():
            existing = p.read_bytes()
            if sha256_bytes(existing) != checksum:
                raise ValueError(f"Artifact overwrite rejected for {ref.key()}")
            return
        p.write_bytes(raw)

    def get(self, ref: ArtifactRef) -> ArtifactEnvelope:
        p = self._path(ref)
        if not p.exists():
            raise KeyError(f"Artifact not found: {ref.key()}")
        data = json.loads(p.read_text(encoding="utf-8"))
        return ArtifactEnvelope.model_validate(data)

    def list(self, kind: str, limit: int = 100) -> List[ArtifactRef]:
        d = self.base_dir / kind
        if not d.exists():
            return []
        refs = []
        for f in sorted(d.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:limit]:
            refs.append(ArtifactRef(kind=kind, artifact_id=f.stem))
        return refs
