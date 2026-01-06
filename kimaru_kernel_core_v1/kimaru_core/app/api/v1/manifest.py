"""Manifest endpoint router (v1)."""

from fastapi import APIRouter, HTTPException

from kimaru_core.app.schema.manifest import ManifestCreateReq, ManifestCreateResp
from kimaru_core.app.services.manifest_service import create_manifest as svc_create_manifest

router = APIRouter(prefix="/api/v1/manifests", tags=["manifests"])


@router.post("", response_model=ManifestCreateResp)
def create_manifest(req: ManifestCreateReq):
    """Create a new manifest with specified zones.
    
    Request body:
    - zones: list of zone IDs (e.g., ['zone1'])
    - name: optional friendly name
    - tenant_id: optional tenant identifier
    
    Returns: manifest_id and file location
    """
    try:
        mid, location = svc_create_manifest(
            zones=req.zones,
            name=req.name,
            tenant_id=req.tenant_id
        )
        return ManifestCreateResp(manifest_id=mid, location=location)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
