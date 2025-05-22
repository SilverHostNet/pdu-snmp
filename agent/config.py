import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# SNMP Configuration
SNMP_HOST = os.getenv("SNMP_HOST", "192.168.1.100")
SNMP_PORT = int(os.getenv("SNMP_PORT", "161"))
SNMP_COMMUNITY = os.getenv("SNMP_COMMUNITY", "public")
SNMP_VERSION = os.getenv("SNMP_VERSION", "2c")

# Supabase Configuration
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

# API Configuration
API_PORT = int(os.getenv("PORT", "5000"))
API_HOST = os.getenv("HOST", "0.0.0.0")
DEBUG = os.getenv("DEBUG", "False").lower() == "true"

# PDU Configuration
PDU_MODEL = os.getenv("PDU_MODEL", "PX3")
PDU_OUTLETS = int(os.getenv("PDU_OUTLETS", "8"))

# Agent Identification
AGENT_ID = os.getenv("AGENT_ID", "")
AGENT_API_KEY = os.getenv("AGENT_API_KEY", "")
