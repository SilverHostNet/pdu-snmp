from fastapi import FastAPI, HTTPException, Request, Response
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from typing import Dict, Any
from snmp_client import SNMPClient
from supabase_client import supabase_client
import config
import json

app = FastAPI(title="SNMP Agent API", description="API for controlling PDU outlets via SNMP")

# Initialize SNMP client
snmp_client = SNMPClient()

# Configure CORS - Updated to be more permissive for troubleshooting
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for development
    allow_credentials=False,  # Set to False to avoid issues with credentials
    allow_methods=["*"],  # Allow all methods
    allow_headers=["*"],  # Allow all headers
    expose_headers=["*"],  # Expose all headers
    max_age=86400  # Cache preflight requests for 24 hours
)

# Helper function to convert SNMP types to standard Python types
def convert_snmp_types(data):
    """Convert SNMP-specific types to standard Python types for JSON serialization"""
    if isinstance(data, dict):
        return {k: convert_snmp_types(v) for k, v in data.items()}
    elif isinstance(data, list):
        return [convert_snmp_types(item) for item in data]
    elif hasattr(data, '__class__') and 'pysnmp.proto.rfc1902' in str(data.__class__):
        # Convert pysnmp types to standard Python types
        return int(data) if 'Integer' in str(data.__class__) or 'Gauge' in str(data.__class__) else str(data)
    else:
        return data


@app.get("/healthz")
async def health_check() -> Dict[str, str]:
    """Health check endpoint"""
    return {"status": "ok"}

@app.get("/outlets")
async def get_outlets() -> Dict[str, Any]:
    """Get all outlets"""
    try:
        result = snmp_client.get_all_outlets()
        # Convert SNMP types to standard Python types
        result = convert_snmp_types(result)
        print(f"Retrieved all outlets: {len(result['outlets'])} outlets found")
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlets: {str(e)}")

@app.get("/outlets/{outlet_id}")
async def get_outlet(outlet_id: str) -> Dict[str, Any]:
    """Get outlet by ID"""
    try:
        result = snmp_client.get_outlet_state(outlet_id)
        
        # Convert SNMP types to standard Python types
        result = convert_snmp_types(result)
        
        # Log the outlet state to Supabase
        if supabase_client.is_connected():
            supabase_client.log_outlet_state(result)
            
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlet {outlet_id}: {str(e)}")

@app.post("/outlets/{outlet_id}/toggle")
async def toggle_outlet(outlet_id: str) -> Dict[str, Any]:
    """Toggle outlet state"""
    try:
        result = snmp_client.toggle_outlet(outlet_id)
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        # Convert SNMP types to standard Python types
        result = convert_snmp_types(result)
        
        # Log the outlet state change to Supabase
        if supabase_client.is_connected():
            supabase_client.log_outlet_state(result)
            
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
        
        # Convert SNMP types to standard Python types
        result = convert_snmp_types(result)
            
        # Log the outlet state change to Supabase
        if supabase_client.is_connected():
            supabase_client.log_outlet_state(result)
            
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
        
        # Convert any SNMP types in the result
        result_data = convert_snmp_types(result["data"])
            
        return result_data
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get outlet history: {str(e)}")

# Enhanced OPTIONS handler for CORS preflight requests
@app.options("/{path:path}")
async def options_handler(request: Request, path: str):
    response = Response()
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type, Authorization, X-Requested-With"
    response.headers["Access-Control-Max-Age"] = "86400"  # 24 hours
    return response

if __name__ == "__main__":
    port = config.API_PORT
    host = config.API_HOST
    debug = config.DEBUG
    print(f"Starting SNMP Agent API on {host}:{port}")
    print(f"PDU IP: {config.SNMP_HOST}, Model: {config.PDU_MODEL}, Outlets: {config.PDU_OUTLETS}")
    print(f"SNMP Version: {config.SNMP_VERSION}, Community: {config.SNMP_COMMUNITY}")
    
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
    
    # Check if HTTPS is enabled
    enable_https = config.ENABLE_HTTPS
    ssl_cert_file = config.SSL_CERT_FILE
    ssl_key_file = config.SSL_KEY_FILE
    
    if enable_https and ssl_cert_file and ssl_key_file:
        print(f"HTTPS enabled with certificates:\n - Cert: {ssl_cert_file}\n - Key: {ssl_key_file}")
        uvicorn.run("main:app", host=host, port=port, reload=debug, ssl_keyfile=ssl_key_file, ssl_certfile=ssl_cert_file)
    else:
        print("Running in HTTP mode (HTTPS not enabled or certificates not configured)")
        uvicorn.run("main:app", host=host, port=port, reload=debug)
