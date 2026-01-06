"""Test script for setup API."""

import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000"

def test_manifest_api():
    """Step 1: Create a manifest."""
    print("\n" + "="*60)
    print("STEP 1: Creating Manifest via /api/v1/manifests")
    print("="*60)
    
    manifest_data = {
        "zones": ["zone1"],
        "name": "test-manifest",
        "tenant_id": "tenant-demo"
    }
    
    print(f"Request payload: {json.dumps(manifest_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/manifests",
            json=manifest_data
        )
        response.raise_for_status()
        
        manifest_resp = response.json()
        print(f"\n✓ Manifest created successfully!")
        print(f"Response: {json.dumps(manifest_resp, indent=2)}")
        
        return manifest_resp
    except Exception as e:
        print(f"✗ Error creating manifest: {e}")
        return None


def test_setup_api(manifest_location):
    """Step 2: Setup session with manifest."""
    print("\n" + "="*60)
    print("STEP 2: Setting up Session via /api/v1/setup")
    print("="*60)
    
    setup_data = {
        "manifest_location": manifest_location,
        "tenant_id": "tenant-demo",
        "session_name": "test-session"
    }
    
    print(f"Request payload: {json.dumps(setup_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/setup",
            json=setup_data
        )
        response.raise_for_status()
        
        setup_resp = response.json()
        print(f"\n✓ Setup successful!")
        print(f"Response: {json.dumps(setup_resp, indent=2)}")
        
        return setup_resp
    except requests.exceptions.HTTPError as e:
        print(f"✗ HTTP Error: {e}")
        print(f"Response: {e.response.text}")
        return None
    except Exception as e:
        print(f"✗ Error during setup: {e}")
        return None


if __name__ == "__main__":
    print("\n" + "="*60)
    print("Testing Setup API Workflow")
    print("="*60)
    
    # Step 1: Create manifest
    manifest_resp = test_manifest_api()
    
    if manifest_resp and "location" in manifest_resp:
        manifest_location = manifest_resp["location"]
        
        # Wait a moment for file to be written
        time.sleep(1)
        
        # Step 2: Setup with manifest
        setup_resp = test_setup_api(manifest_location)
        
        if setup_resp:
            print("\n" + "="*60)
            print("✓ Full workflow completed successfully!")
            print("="*60)
            print(f"\nSession ID: {setup_resp.get('session_id')}")
            print(f"Tenant ID: {setup_resp.get('tenant_id')}")
            print(f"Zones Loaded: {setup_resp.get('zones_loaded')}")
            print(f"Created At: {setup_resp.get('created_at')}")
    else:
        print("\nCannot proceed to setup without manifest location")
