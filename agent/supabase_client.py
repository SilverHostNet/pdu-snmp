import os
import requests
import json
from typing import Dict, Any, List, Optional
import config
from datetime import datetime

class SupabaseClient:
    def __init__(self):
        # Load configuration from config.py
        self.supabase_url = config.SUPABASE_URL
        self.supabase_key = config.SUPABASE_SERVICE_KEY
        self._connected = False
        
        # Check if we have the required configuration
        if self.supabase_url and self.supabase_key:
            self._connected = self._test_connection()
    
    def is_connected(self) -> bool:
        """Check if Supabase connection is available"""
        return self._connected
    
    def _test_connection(self) -> bool:
        """Test the connection to Supabase"""
        try:
            # Try to fetch a single row from agents table
            response = self._request("GET", "agents?limit=1")
            return response.status_code == 200
        except Exception as e:
            print(f"Supabase connection test failed: {e}")
            return False
    
    def _request(self, method: str, endpoint: str, data: Optional[Dict[str, Any]] = None) -> requests.Response:
        """Make a request to the Supabase REST API"""
        url = f"{self.supabase_url}/rest/v1/{endpoint}"
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}",
            "Content-Type": "application/json",
            "Prefer": "return=representation"
        }
        
        if method == "GET":
            return requests.get(url, headers=headers)
        elif method == "POST":
            return requests.post(url, headers=headers, json=data)
        elif method == "PUT":
            return requests.put(url, headers=headers, json=data)
        elif method == "PATCH":
            return requests.patch(url, headers=headers, json=data)
        elif method == "DELETE":
            return requests.delete(url, headers=headers)
        else:
            raise ValueError(f"Unsupported HTTP method: {method}")
    
    def update_agent_status(self, status: str = "connected") -> Dict[str, Any]:
        """Update the agent status in the database"""
        if not self._connected:
            return {"success": False, "message": "Supabase connection not available"}
        
        try:
            # Check if agent exists
            response = self._request("GET", f"agents?host=eq.{config.API_HOST}&port=eq.{config.API_PORT}&limit=1")
            
            if response.status_code == 200 and len(response.json()) > 0:
                # Update existing agent
                agent_id = response.json()[0]["id"]
                update_data = {
                    "status": status,
                    "updated_at": datetime.now().isoformat()
                }
                update_response = self._request("PATCH", f"agents?id=eq.{agent_id}", update_data)
                return {"success": update_response.status_code == 200, "message": "Agent status updated"}
            else:
                # Create new agent
                agent_data = {
                    "name": "Local Agent",
                    "host": config.API_HOST,
                    "port": config.API_PORT,
                    "status": status
                }
                create_response = self._request("POST", "agents", agent_data)
                return {"success": create_response.status_code == 201, "message": "Agent created"}
        except Exception as e:
            print(f"Error updating agent status: {e}")
            return {"success": False, "message": str(e)}
    
    def log_outlet_state(self, outlet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log outlet state to the database"""
        if not self._connected:
            return {"success": False, "message": "Supabase connection not available"}
        
        try:
            # Get agent ID
            agent_response = self._request("GET", f"agents?host=eq.{config.API_HOST}&port=eq.{config.API_PORT}&limit=1")
            
            if agent_response.status_code != 200 or len(agent_response.json()) == 0:
                return {"success": False, "message": "Agent not found in database"}
            
            agent_id = agent_response.json()[0]["id"]
            
            # Get device ID (PDU)
            device_response = self._request("GET", f"devices?agent_id=eq.{agent_id}&host=eq.{config.SNMP_HOST}&limit=1")
            
            device_id = None
            if device_response.status_code == 200 and len(device_response.json()) > 0:
                device_id = device_response.json()[0]["id"]
            else:
                # Create device if it doesn't exist
                device_data = {
                    "name": f"{config.PDU_MODEL} PDU",
                    "host": config.SNMP_HOST,
                    "snmp_community": config.SNMP_COMMUNITY,
                    "snmp_version": config.SNMP_VERSION,
                    "agent_id": agent_id
                }
                device_create_response = self._request("POST", "devices", device_data)
                if device_create_response.status_code == 201:
                    device_id = device_create_response.json()[0]["id"]
                else:
                    return {"success": False, "message": "Failed to create device"}
            
            # Log outlet reading
            reading_data = {
                "device_id": device_id,
                "outlet_number": int(outlet_data["id"]),
                "state": outlet_data["state"],
                "voltage": outlet_data["voltage"],
                "current": outlet_data["current"]
            }
            
            reading_response = self._request("POST", "outlet_readings", reading_data)
            return {"success": reading_response.status_code == 201, "message": "Outlet state logged"}
        except Exception as e:
            print(f"Error logging outlet state: {e}")
            return {"success": False, "message": str(e)}
    
    def get_outlet_history(self, outlet_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get outlet history from the database"""
        if not self._connected:
            return {"success": False, "message": "Supabase connection not available"}
        
        try:
            # Get device ID for the current PDU
            agent_response = self._request("GET", f"agents?host=eq.{config.API_HOST}&port=eq.{config.API_PORT}&limit=1")
            
            if agent_response.status_code != 200 or len(agent_response.json()) == 0:
                return {"success": False, "message": "Agent not found in database"}
            
            agent_id = agent_response.json()[0]["id"]
            
            device_response = self._request("GET", f"devices?agent_id=eq.{agent_id}&host=eq.{config.SNMP_HOST}&limit=1")
            
            if device_response.status_code != 200 or len(device_response.json()) == 0:
                return {"success": False, "message": "Device not found in database"}
            
            device_id = device_response.json()[0]["id"]
            
            # Get outlet readings
            readings_response = self._request(
                "GET", 
                f"outlet_readings?device_id=eq.{device_id}&outlet_number=eq.{outlet_id}&order=created_at.desc&limit={limit}"
            )
            
            if readings_response.status_code != 200:
                return {"success": False, "message": "Failed to fetch outlet readings"}
            
            return {"success": True, "data": {"readings": readings_response.json()}}
        except Exception as e:
            print(f"Error getting outlet history: {e}")
            return {"success": False, "message": str(e)}

# Create a singleton instance
supabase_client = SupabaseClient()
