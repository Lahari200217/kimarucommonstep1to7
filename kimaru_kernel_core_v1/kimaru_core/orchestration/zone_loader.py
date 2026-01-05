from __future__ import annotations
import importlib
from typing import Dict, List, Optional

from kimaru_core.orchestration.zone_kernel_interface import ZoneKernel
from kimaru_core.runtime.manifest import KimaruManifest, ZoneKernelRef

class ZoneKernelLoader:
    """Loads ZoneKernel plugins from a KimaruManifest.

    Manifest entrypoint format:
      - "some.module:SomeZoneKernelClass"
      - "some.module:create" (callable returning ZoneKernel)
    """

    def __init__(self, manifest: KimaruManifest):
        self.manifest = manifest
        self._loaded: Dict[str, ZoneKernel] = {}

    def discover(self) -> List[ZoneKernelRef]:
        return [z for z in self.manifest.zones if z.enabled]

    def load(self, zone_id: str) -> ZoneKernel:
        if zone_id in self._loaded:
            return self._loaded[zone_id]

        ref = next((z for z in self.discover() if z.zone_id == zone_id), None)
        if ref is None:
            raise ValueError(f"Zone '{zone_id}' not found/enabled in manifest")

        module_name, symbol = ref.entrypoint.split(":")
        mod = importlib.import_module(module_name)
        obj = getattr(mod, symbol)

        if isinstance(obj, type):
            kernel = obj(**ref.config)  # type: ignore[arg-type]
        else:
            kernel = obj(**ref.config)  # factory callable

        if not isinstance(kernel, ZoneKernel):
            raise TypeError(f"Entrypoint {ref.entrypoint} did not return a ZoneKernel")

        if kernel.zone_id() != zone_id:
            raise ValueError(f"Loaded kernel zone_id mismatch: expected {zone_id}, got {kernel.zone_id()}")

        self._loaded[zone_id] = kernel
        return kernel

    def bootstrap_all(self) -> Dict[str, ZoneKernel]:
        for z in self.discover():
            self.load(z.zone_id)
        return dict(self._loaded)
