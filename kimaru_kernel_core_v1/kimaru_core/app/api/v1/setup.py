"""Setup endpoint router (v1)."""

from fastapi import APIRouter, HTTPException

from kimaru_core.app.schema.setup import SetupReq, SetupResp
from kimaru_core.app.services.setup_service import setup_session

router = APIRouter(prefix="/api/v1/setup", tags=["setup"])


@router.post("", response_model=SetupResp)
def setup(req: SetupReq):
    
    try:
        session_id, tenant_id, zones_loaded, created_at, manifest_id, state = setup_session(
            manifest_location=req.manifest_location,
            tenant_id=req.tenant_id,
            session_name=req.session_name
        )
        
        return SetupResp(
            session_id=session_id,
            tenant_id=tenant_id,
            manifest_id=manifest_id,
            zones_loaded=zones_loaded,
            created_at=created_at,
            state={
                "zones": list(state.get("zones", {}).keys()),
                "has_run_coordinator": state.get("run_coordinator") is not None,
            }
        )
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ValueError as e:
        raise HTTPException(status_code=400, detail=f"Invalid setup request: {str(e)}")
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Setup failed: {str(e)}")
