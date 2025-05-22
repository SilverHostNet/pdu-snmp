# Deploying a Remote/Offsite SNMP Agent

This guide explains how to deploy the SNMP agent on a remote server or VM that has network access to your PDU devices.

## Prerequisites

1. Ubuntu 20.04 or newer server/VM
2. Python 3.8 or newer
3. Network access to the PDU device
4. Internet access for the agent to connect to Supabase

## Step 1: Prepare the Server

```bash
# Update the system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install -y python3-pip python3-venv git
```

## Step 2: Clone or Copy the Agent Code

```bash
# Option 1: Clone from Git repository (if available)
git clone https://your-repository-url.git
cd your-repository-name/agent

# Option 2: Create directory and copy files manually
mkdir -p ~/snmp-agent
cd ~/snmp-agent
# Copy all agent files to this directory
```

## Step 3: Set Up Python Environment

```bash
# Create a virtual environment
python3 -m venv venv

# Activate the virtual environment
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## Step 4: Configure the Agent

```bash
# Copy the example .env file
cp .env.example .env

# Edit the .env file with your configuration
nano .env
```

Update the following values in the .env file:

```
# SNMP Configuration
SNMP_HOST=<your-pdu-ip-address>
SNMP_PORT=161
SNMP_COMMUNITY=<your-snmp-community>
SNMP_VERSION=2c

# Supabase Configuration
SUPABASE_URL=<your-supabase-url>
SUPABASE_SERVICE_KEY=<your-supabase-service-key>

# API Configuration
PORT=5000
HOST=0.0.0.0
DEBUG=False

# PDU Configuration
PDU_MODEL=PX3
PDU_OUTLETS=8

# Agent Identification (optional)
AGENT_ID=<unique-identifier-for-this-agent>
AGENT_API_KEY=<api-key-for-authentication>
```

## Step 5: Test the Agent

```bash
# Make sure you're in the agent directory with the virtual environment activated
python main.py
```

Verify that the agent starts correctly and can connect to both the PDU and Supabase.

## Step 6: Set Up as a System Service

```bash
# Copy the service file to systemd directory
sudo cp agent.service /etc/systemd/system/

# Edit the service file if needed (adjust paths)
sudo nano /etc/systemd/system/agent.service

# Reload systemd
sudo systemctl daemon-reload

# Enable the service to start on boot
sudo systemctl enable agent.service

# Start the service
sudo systemctl start agent.service

# Check the status
sudo systemctl status agent.service
```

## Step 7: Configure Firewall (Optional but Recommended)

```bash
# Allow the agent API port
sudo ufw allow 5000/tcp

# Enable the firewall if not already enabled
sudo ufw enable
```

## Step 8: Update Agent Settings in Web UI

1. Log in to the web application
2. Navigate to Dashboard > Settings
3. Update the Agent Host to the IP address or hostname of your remote server
4. Update the Agent Port (default is 5000)
5. Click "Test Connection" to verify connectivity
6. Save the settings

## Troubleshooting

### Checking Logs

```bash
# View service logs
sudo journalctl -u agent.service -f

# View application logs
cat ~/snmp-agent/agent_service.log
```

### Common Issues

1. **Connection Refused**: Ensure the firewall allows traffic on the agent port
2. **SNMP Timeout**: Verify network connectivity to the PDU and check SNMP community string
3. **Supabase Connection Failed**: Check internet connectivity and Supabase credentials

### Restarting the Agent

```bash
sudo systemctl restart agent.service
```

## Security Considerations

1. Use a dedicated user for running the agent service
2. Consider using HTTPS with a reverse proxy (Nginx/Apache) for the agent API
3. Implement API key authentication for the agent endpoints
4. Restrict network access to the PDU device
5. Use strong, unique passwords for all accounts
