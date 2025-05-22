from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Dict, Any
from snmp_client import SNMPClient
import config

app = FastAPI(title="SNMP Agent API", description="API for controlling PDU outlets via SNMP")

# Initialize SNMP client
snmp_client = SNMPClient()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/outlets")
async def get_outlets() -> Dict[str, Any]:
    """Get all outlets"""
    try:
        return snmp_client.get_all_outlets()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlets: {str(e)}")

@app.get("/outlets/{outlet_id}")
async def get_outlet(outlet_id: str) -> Dict[str, Any]:
    """Get outlet by ID"""
    try:
        return snmp_client.get_outlet_state(outlet_id)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlet {outlet_id}: {str(e)}")

@app.post("/outlets/{outlet_id}/toggle")
async def toggle_outlet(outlet_id: str) -> Dict[str, Any]:
    """Toggle outlet state"""
    try:
        result = snmp_client.toggle_outlet(outlet_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to toggle outlet {outlet_id}: {str(e)}")

@app.post("/outlets/{outlet_id}/cycle")
async def cycle_outlet(outlet_id: str) -> Dict[str, Any]:
    """Cycle outlet (turn off then on)"""
    try:
        result = snmp_client.cycle_outlet(outlet_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to cycle outlet {outlet_id}: {str(e)}")

# Add endpoint to get outlet history from Supabase
@app.get("/outlets/{outlet_id}/history")
async def get_outlet_history(outlet_id: str, limit: int = 100) -> Dict[str, Any]:
    """Get outlet history from Supabase"""
    try:
        if not supabase_client.is_connected():
            raise HTTPException(status_code=503, detail="Supabase connection not available")
            
        result = supabase_client.get_outlet_history(outlet_id, limit)
        if not result["success"]:
            raise HTTPException(status_code=500, detail=result["message"])
            
        return result["data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlet history: {str(e)}")

if __name__ == "__main__":
    port = config.API_PORT
    host = config.API_HOST
    debug = config.DEBUG
    print(f"Starting SNMP Agent API on {host}:{port}")
    print(f"PDU IP: {config.SNMP_HOST}, Model: {config.PDU_MODEL}, Outlets: {config.PDU_OUTLETS}")
    
    # Log Supabase connection status
    if supabase_client.is_connected():
        print(f"Supabase connected: {config.SUPABASE_URL}")
        # Update agent status in Supabase
        status_result = supabase_client.update_agent_status("connected")
        if status_result["success"]:
            print("Agent status updated in Supabase")
        else:
            print(f"Failed to update agent status: {status_result['message']}")
    else:
        print("Supabase not connected. Set SUPABASE_URL and SUPABASE_SERVICE_KEY in .env file to enable database logging.")
    
    uvicorn.run("main:app", host=host, port=port, reload=debug)
