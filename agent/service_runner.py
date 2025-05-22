#!/usr/bin/env python3

import os
import sys
import time
import signal
import subprocess
import logging
from datetime import datetime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("agent_service.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger("agent_service")

# Path to the main.py script
MAIN_SCRIPT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "main.py")

# Process handle
process = None

def start_agent():
    """Start the agent process"""
    global process
    try:
        logger.info("Starting SNMP agent...")
        # Start the process
        process = subprocess.Popen(
            [sys.executable, MAIN_SCRIPT],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        logger.info(f"Agent started with PID {process.pid}")
        return True
    except Exception as e:
        logger.error(f"Failed to start agent: {e}")
        return False

def stop_agent():
    """Stop the agent process"""
    global process
    if process:
        try:
            logger.info("Stopping SNMP agent...")
            process.terminate()
            process.wait(timeout=5)
            logger.info("Agent stopped")
        except subprocess.TimeoutExpired:
            logger.warning("Agent did not terminate gracefully, forcing...")
            process.kill()
        except Exception as e:
            logger.error(f"Error stopping agent: {e}")
        finally:
            process = None

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {sig}, shutting down...")
    stop_agent()
    sys.exit(0)

def monitor_process():
    """Monitor the agent process and restart if it crashes"""
    global process
    if process:
        return_code = process.poll()
        if return_code is not None:
            logger.warning(f"Agent process exited with code {return_code}, restarting...")
            # Read any output from the process
            stdout, stderr = process.communicate()
            if stdout:
                logger.info(f"Agent stdout: {stdout}")
            if stderr:
                logger.error(f"Agent stderr: {stderr}")
            process = None
            time.sleep(5)  # Wait before restarting
            start_agent()

def main():
    """Main service runner"""
    # Register signal handlers
    signal.signal(signal.SIGTERM, signal_handler)
    signal.signal(signal.SIGINT, signal_handler)
    
    logger.info("Agent service runner started")
    
    # Start the agent
    if not start_agent():
        logger.error("Failed to start agent, exiting")
        return 1
    
    # Monitor the process
    try:
        while True:
            monitor_process()
            time.sleep(5)  # Check every 5 seconds
    except Exception as e:
        logger.error(f"Error in monitor loop: {e}")
        stop_agent()
        return 1
    finally:
        stop_agent()
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
