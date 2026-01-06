"""Manifest creation service."""

import json
import os
from pathlib import Path
from typing import List, Optional, Tuple

from kimaru_core.utils.ids import new_id
from kimaru_core.utils.time import utc_now_iso


def _base_var_dir() -> Path:
    """Get the base variable directory for storing manifests."""
    return Path(os.getenv("KIMARU_VAR_DIR", Path.cwd() / "var"))


def create_manifest(
    zones: List[str],
    name: Optional[str] = None,
    tenant_id: Optional[str] = None
) -> Tuple[str, str]:
    """Create a JSON manifest file with specified zones.
    
    Args:
        zones: List of zone IDs (e.g., ['zone1', 'zone2'])
        name: Optional friendly name for the manifest
        tenant_id: Optional tenant/client identifier
        
    Returns:
        Tuple of (manifest_id, file_path)
    """
    mid = new_id("manifest")
    payload = {
        "manifest_id": mid,
        "name": name or mid,
        "tenant_id": tenant_id,
        "zones": zones,
        "created_at": utc_now_iso(),
    }
    
    base = _base_var_dir()
    manifests_dir = base / "manifests"
    manifests_dir.mkdir(parents=True, exist_ok=True)
    
    path = manifests_dir / f"{mid}.json"
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=2)
    
    return mid, str(path)
