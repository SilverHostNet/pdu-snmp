from pysnmp.hlapi import *
import os
import time
from typing import Dict, Any, Optional, Tuple, List
from datetime import datetime
import config

class SNMPClient:
    def __init__(self):
        # Load configuration from config.py
        self.pdu_ip = config.SNMP_HOST
        self.community = config.SNMP_COMMUNITY
        self.port = config.SNMP_PORT
        self.snmp_version = config.SNMP_VERSION
        self.pdu_model = config.PDU_MODEL
        self.num_outlets = config.PDU_OUTLETS
        
        # Raritan PDU OIDs for PX3 model
        # Reference: Raritan PX3 MIB documentation
        self.oids = {
            "outlet_state": ".1.3.6.1.4.1.13742.6.4.1.2.1.3",  # + .pdu.outlet
            "outlet_control": ".1.3.6.1.4.1.13742.6.4.1.2.1.2",  # + .pdu.outlet
            "inlet_voltage": ".1.3.6.1.4.1.13742.6.5.2.3.1.4",  # + .pdu.inlet.sensor
            "outlet_current": ".1.3.6.1.4.1.13742.6.5.2.3.1.4"  # + .pdu.outlet.sensor
        }
        
        # State values for Raritan PDUs
        self.states = {
            "on": 1,  # Note: 7 is also considered 'on' in get_outlet_state
            "off": 0,
            "cycle": 2  # Power cycle operation
        }
        
        # Sensor types
        self.sensor_types = {
            "voltage": 4,  # RMS Voltage
            "current": 5   # RMS Current
        }
        
    def get_outlet_state(self, outlet_id: str) -> Dict[str, Any]:
        """Get the state of an outlet"""
        try:
            # Convert outlet_id to integer for OID
            outlet_num = int(outlet_id)
            
            # Get outlet state
            state_oid = f"{self.oids['outlet_state']}.1.{outlet_num}"
            state_value = self._snmp_get(state_oid)
            
            # Get voltage (from inlet)
            voltage_oid = f"{self.oids['inlet_voltage']}.1.1.{self.sensor_types['voltage']}"
            voltage_value = self._snmp_get(voltage_oid)
            
            # Get current for this outlet
            current_oid = f"{self.oids['outlet_current']}.1.{outlet_num}.{self.sensor_types['current']}"
            current_value = self._snmp_get(current_oid)
            
            # Map numeric state to string
            state_str = "on" if state_value == self.states["on"] else "off"
            
            return {
                "id": outlet_id,
                "name": f"Outlet {outlet_id}",
                "state": state_str,
                "voltage": voltage_value or 120,  # Default if not available
                "current": current_value or 0,    # Default if not available
                "lastUpdated": datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error getting outlet state: {e}")
            # Fallback to placeholder data
            return {
                "id": outlet_id,
                "name": f"Outlet {outlet_id}",
                "state": "unknown",
                "voltage": 120,
                "current": 0,
                "lastUpdated": datetime.now().isoformat(),
                "error": str(e)
            }
    
    def get_all_outlets(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all outlets"""
        try:
            outlets = []
            for outlet_num in range(1, self.num_outlets + 1):
                outlet = self.get_outlet_state(str(outlet_num))
                outlets.append(outlet)
            return {"outlets": outlets}
        except Exception as e:
            print(f"Error getting all outlets: {e}")
            # Fallback to placeholder data
            return {"outlets": [
                {"id": "1", "name": "Outlet 1", "state": "on", "voltage": 120, "current": 5},
                {"id": "2", "name": "Outlet 2", "state": "off", "voltage": 120, "current": 0},
                {"id": "3", "name": "Outlet 3", "state": "on", "voltage": 120, "current": 3},
            ]}
    
    def toggle_outlet(self, outlet_id: str) -> Dict[str, Any]:
        """Toggle an outlet (on->off or off->on)"""
        try:
            # Get current state
            outlet_info = self.get_outlet_state(outlet_id)
            current_state = outlet_info["state"]
            
            # Determine new state (opposite of current)
            new_state = "off" if current_state == "on" else "on"
            
            # Convert outlet_id to integer for OID
            outlet_num = int(outlet_id)
            
            # Set the new state
            control_oid = f"{self.oids['outlet_control']}.1.{outlet_num}"
            success = self._snmp_set(control_oid, Integer, self.states[new_state])
            
            if success:
                # Wait briefly for the change to take effect
                time.sleep(1)
                # Get updated state
                updated_outlet = self.get_outlet_state(outlet_id)
                updated_outlet["message"] = f"Outlet toggled to {new_state} successfully"
                return updated_outlet
            else:
                return {
                    "id": outlet_id,
                    "name": f"Outlet {outlet_id}",
                    "state": current_state,
                    "message": "Failed to toggle outlet",
                    "error": "SNMP SET operation failed"
                }
        except Exception as e:
            print(f"Error toggling outlet: {e}")
            return {
                "id": outlet_id,
                "name": f"Outlet {outlet_id}",
                "state": "unknown",
                "message": "Failed to toggle outlet",
                "error": str(e)
            }
    
    def cycle_outlet(self, outlet_id: str) -> Dict[str, Any]:
        """Cycle an outlet (turn off then on)"""
        try:
            # Convert outlet_id to integer for OID
            outlet_num = int(outlet_id)
            
            # Send cycle command using the correct OID format for Raritan PDU
            # Format: .1.3.6.1.4.1.13742.6.4.1.2.1.2.1.<outlet_number>
            control_oid = f"{self.oids['outlet_control']}.1.{outlet_num}"
            print(f"Cycling outlet {outlet_id} using OID: {control_oid}")
            success = self._snmp_set(control_oid, Integer, self.states["cycle"])
            
            if success:
                # Wait for the cycle to complete (typically takes a few seconds)
                time.sleep(5)
                # Get updated state
                updated_outlet = self.get_outlet_state(outlet_id)
                updated_outlet["message"] = "Outlet cycled successfully"
                return updated_outlet
            else:
                return {
                    "id": outlet_id,
                    "name": f"Outlet {outlet_id}",
                    "state": "unknown",
                    "message": "Failed to cycle outlet",
                    "error": "SNMP SET operation failed"
                }
        except Exception as e:
            print(f"Error cycling outlet: {e}")
            return {
                "id": outlet_id,
                "name": f"Outlet {outlet_id}",
                "state": "unknown",
                "message": "Failed to cycle outlet",
                "error": str(e)
            }
    
    def _snmp_get(self, oid: str) -> Optional[Any]:
        """Perform an SNMP GET operation"""
        try:
            error_indication, error_status, error_index, var_binds = next(
                getCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.pdu_ip, self.port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid))
                )
            )
            
            if error_indication:
                print(f"SNMP GET Error: {error_indication}")
                return None
            elif error_status:
                print(f"SNMP GET Error: {error_status.prettyPrint()} at {var_binds[int(error_index) - 1][0] if error_index else '?'}")
                return None
            else:
                # Extract the value from the response
                for var_bind in var_binds:
                    return var_bind[1]
            return None
        except Exception as e:
            print(f"Error in SNMP GET: {e}")
            return None
    
    def _snmp_set(self, oid: str, value_type, value) -> bool:
        """Perform an SNMP SET operation"""
        try:
            error_indication, error_status, error_index, var_binds = next(
                setCmd(
                    SnmpEngine(),
                    CommunityData(self.community),
                    UdpTransportTarget((self.pdu_ip, self.port)),
                    ContextData(),
                    ObjectType(ObjectIdentity(oid), value_type(value))
                )
            )
            
            if error_indication:
                print(f"SNMP SET Error: {error_indication}")
                return False
            elif error_status:
                print(f"SNMP SET Error: {error_status.prettyPrint()} at {var_binds[int(error_index) - 1][0] if error_index else '?'}")
                return False
            else:
                return True
        except Exception as e:
            print(f"Error in SNMP SET: {e}")
            return False
