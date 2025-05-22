import os
import json
from typing import Dict, Any, List
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class SupabaseClient:
    def __init__(self):
        # Import here to avoid requiring the package if not using Supabase
        from supabase import create_client
        
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        
        if not self.supabase_url or not self.supabase_key:
            print("WARNING: Supabase URL or key not configured. Database operations will be skipped.")
            self.client = None
        else:
            try:
                self.client = create_client(self.supabase_url, self.supabase_key)
                print(f"Supabase client initialized with URL: {self.supabase_url}")
            except Exception as e:
                print(f"Error initializing Supabase client: {e}")
                self.client = None
    
    def is_connected(self) -> bool:
        """Check if Supabase client is initialized"""
        return self.client is not None
    
    def log_outlet_reading(self, outlet_data: Dict[str, Any]) -> Dict[str, Any]:
        """Log outlet reading to Supabase"""
        if not self.is_connected():
            return {"success": False, "message": "Supabase client not initialized"}
        
        try:
            # Convert outlet data to the format expected by the database
            reading = {
                "outlet_id": outlet_data.get("outlet_id"),
                "state": outlet_data["state"],
                "voltage": outlet_data["voltage"],
                "current": outlet_data["current"],
                "created_at": datetime.now().isoformat()
            }
            
            # Insert into outlet_readings table
            result = self.client.table("outlet_readings").insert(reading).execute()
            
            return {"success": True, "data": result}
        except Exception as e:
            print(f"Error logging outlet reading to Supabase: {e}")
            return {"success": False, "message": str(e)}
    
    def log_outlet_event(self, outlet_id: str, event_type: str, new_state: str = None, user_initiated: bool = True) -> Dict[str, Any]:
        """Log outlet event to Supabase"""
        if not self.is_connected():
            return {"success": False, "message": "Supabase client not initialized"}
        
        try:
            # Prepare event data
            event = {
                "outlet_id": outlet_id,
                "event_type": event_type,
                "user_initiated": user_initiated
            }
            
            # Add new_state if provided
            if new_state:
                event["new_state"] = new_state
            
            # Insert into outlet_events table
            result = self.client.table("outlet_events").insert(event).execute()
            
            return {"success": True, "data": result}
        except Exception as e:
            print(f"Error logging outlet event to Supabase: {e}")
            return {"success": False, "message": str(e)}
    
    def get_outlet_history(self, outlet_id: str, limit: int = 100) -> Dict[str, Any]:
        """Get outlet reading history from Supabase"""
        if not self.is_connected():
            return {"success": False, "message": "Supabase client not initialized"}
        
        try:
            # Query outlet_readings table
            result = self.client.table("outlet_readings") \
                .select("*") \
                .eq("outlet_id", outlet_id) \
                .order("created_at", desc=True) \
                .limit(limit) \
                .execute()
            
            return {"success": True, "data": result}
        except Exception as e:
            print(f"Error getting outlet history from Supabase: {e}")
            return {"success": False, "message": str(e)}
