from __future__ import annotations
from pathlib import Path
import json

from kimaru_core.runtime.boot_manager import BootManager, BootConfig
from kimaru_core.runtime.manifest import KimaruManifest, ZoneKernelRef


def pretty_print(title: str, obj):
    print(f"--- {title} ---")
    try:
        print(json.dumps(obj, default=str, indent=2))
    except Exception:
        print(obj)
    print()


def demo():
    var_dir = Path.cwd() / "var_demo"
   
    bm = BootManager(BootConfig(var_dir=var_dir, manifest=None))
    state = bm.boot()
    pretty_print("Core booted (no manifest). Zones", list(state.get("zones", {}).keys()))
    manifest = KimaruManifest(
        core_version="0.1.0",
        zones=[
            ZoneKernelRef(
                zone_id="zone1",
                package="kimaru_core",
                entrypoint="kimaru_core.orchestration.zone1_example:Zone1Kernel",
                version="0.1.0",
                enabled=True,
            )
        ],
    )

    bm2 = BootManager(BootConfig(var_dir=var_dir, manifest=manifest))
    state2 = bm2.boot()
    pretty_print("Core booted (with manifest). Zones loaded", list(state2.get("zones", {}).keys()))
    zones = state2.get("zones", {})
    if "zone1" in zones:
        z = zones["zone1"]
        pretty_print("Zone1 id/version", {"zone_id": z.zone_id(), "version": z.kernel_version()})


if __name__ == "__main__":
    demo()