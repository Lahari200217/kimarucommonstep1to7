"""Setup service for session initialization."""

import json
import os
from pathlib import Path
from typing import Dict, List, Tuple, Any

from kimaru_core.utils.ids import new_id
from kimaru_core.utils.time import utc_now_iso
from kimaru_core.runtime.boot_manager import BootManager, BootConfig
from kimaru_core.runtime.manifest import KimaruManifest, ZoneKernelRef


def _base_var_dir() -> Path:
    """Get the base variable directory."""
    return Path(os.getenv("KIMARU_VAR_DIR", Path.cwd() / "var"))


def load_manifest_from_file(manifest_location: str) -> Dict[str, Any]:
  
    path = Path(manifest_location)
    
    if not path.exists():
        raise FileNotFoundError(f"Manifest file not found: {manifest_location}")
    
    try:
        with open(path, "r", encoding="utf-8") as fh:
            manifest_data = json.load(fh)
        return manifest_data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON in manifest: {e}")


def setup_session(
    manifest_location: str,
    tenant_id: str = None,
    session_name: str = None
) -> Tuple[str, str, List[str], str, str, Dict[str, Any]]:

    manifest_data = load_manifest_from_file(manifest_location)
    
    # Extract manifest info
    manifest_id = manifest_data.get("manifest_id", new_id("manifest"))
    zones = manifest_data.get("zones", [])
    
    # Use provided tenant_id or from manifest
    if not tenant_id:
        tenant_id = manifest_data.get("tenant_id", new_id("tenant"))
    
    # Create session ID
    session_id = new_id("session")
    created_at = utc_now_iso()
    
    # Default zone mappings for known zones
    zone_mappings = {
        "zone1": {
            "package": "kimaru_core",
            "entrypoint": "kimaru_core.orchestration.zone1_example:Zone1Kernel",
        }
    }
    
    # Build KimaruManifest object from loaded zones
    zone_refs = []
    for zone_info in zones:
        # If zone_info is just a string (zone_id), use default package/entrypoint
        if isinstance(zone_info, str):
            zone_id = zone_info
            # Use predefined mapping or fallback
            if zone_id in zone_mappings:
                mapping = zone_mappings[zone_id]
                zone_refs.append(ZoneKernelRef(
                    zone_id=zone_id,
                    package=mapping["package"],
                    entrypoint=mapping["entrypoint"],
                    version="0.1.0",
                    enabled=True,
                ))
            else:
                raise ValueError(f"Unknown zone: {zone_id}. Supported zones: {list(zone_mappings.keys())}")
        elif isinstance(zone_info, dict):
            # Full zone configuration provided
            zone_refs.append(ZoneKernelRef(**zone_info))
    
    kimaru_manifest = KimaruManifest(
        core_version=manifest_data.get("core_version", "0.1.0"),
        zones=zone_refs,
        federation=manifest_data.get("federation", {})
    )
    
    # Boot the core with manifest
    var_dir = _base_var_dir()
    boot_config = BootConfig(var_dir=var_dir, manifest=kimaru_manifest)
    boot_manager = BootManager(boot_config)
    
    try:
        state = boot_manager.boot()
    except Exception as e:
        raise RuntimeError(f"Failed to boot core with manifest: {e}")
    
    # Extract loaded zones
    zones_loaded = list(state.get("zones", {}).keys())
    
    # Store session info
    session_data = {
        "session_id": session_id,
        "tenant_id": tenant_id,
        "manifest_id": manifest_id,
        "manifest_location": manifest_location,
        "zones_loaded": zones_loaded,
        "created_at": created_at,
        "run_coordinator": state.get("run_coordinator") is not None,
    }
    
    # Optionally store session to db
    base = _base_var_dir()
    sessions_dir = base / "sessions"
    sessions_dir.mkdir(parents=True, exist_ok=True)
    
    session_file = sessions_dir / f"{session_id}.json"
    with open(session_file, "w", encoding="utf-8") as fh:
        json.dump(session_data, fh, indent=2)
    
    return session_id, tenant_id, zones_loaded, created_at, manifest_id, state
