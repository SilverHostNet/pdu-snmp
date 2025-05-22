# SNMP Agent for PDU Control

This is a FastAPI-based agent that provides an API for controlling PDU outlets via SNMP.

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Create a `.env` file based on `.env.example` and configure your SNMP and Supabase settings.

3. Run the agent:

```bash
python main.py
```

Or use the service runner for production:

```bash
python service_runner.py
```

## API Endpoints

- `GET /healthz` - Health check endpoint
- `GET /outlets` - Get all outlets
- `GET /outlets/{outlet_id}` - Get outlet by ID
- `POST /outlets/{outlet_id}/toggle` - Toggle outlet state
- `POST /outlets/{outlet_id}/cycle` - Cycle outlet (turn off then on)

## SNMP Implementation

The `snmp_client.py` file contains the SNMP client implementation. Currently, it contains placeholder methods that should be replaced with actual SNMP operations using the pysnmp library.

## Configuration

The `config.py` file loads configuration from environment variables. See `.env.example` for available options.

## Service Runner

The `service_runner.py` script provides a way to run the agent as a service with automatic restart on failure.
