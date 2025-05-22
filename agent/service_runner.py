import os
import sys
import time
import signal
import subprocess
import logging

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('service.log')
    ]
)

logger = logging.getLogger("service_runner")

# Configuration
MAX_RESTARTS = 5
RESTART_DELAY = 5  # seconds
MAX_RUNTIME = 24 * 60 * 60  # 24 hours in seconds

class ServiceRunner:
    def __init__(self, command):
        self.command = command
        self.process = None
        self.running = False
        self.restart_count = 0
        self.start_time = time.time()
        
    def start(self):
        """Start the service"""
        logger.info(f"Starting service: {self.command}")
        self.process = subprocess.Popen(
            self.command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            universal_newlines=True
        )
        self.running = True
        
    def stop(self):
        """Stop the service"""
        if self.process and self.running:
            logger.info("Stopping service")
            self.process.terminate()
            try:
                self.process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                logger.warning("Service did not terminate gracefully, forcing kill")
                self.process.kill()
            self.running = False
            
    def restart(self):
        """Restart the service"""
        self.stop()
        time.sleep(1)  # Give it a moment to fully stop
        self.start()

def signal_handler(sig, frame):
    """Handle termination signals"""
    logger.info(f"Received signal {sig}, shutting down")
    if runner:
        runner.stop()
    sys.exit(0)

if __name__ == "__main__":
    # Register signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Command to run the FastAPI app
    cmd = "python main.py"
    
    # Create and start the service runner
    runner = ServiceRunner(cmd)
    runner.start()
    
    try:
        # Keep the script running
        while runner.running:
            time.sleep(1)
            
            # Check if process is still alive
            if runner.process.poll() is not None:
                # Check if we should restart
                if runner.restart_count < MAX_RESTARTS:
                    logger.error(f"Service has stopped unexpectedly, restarting (attempt {runner.restart_count + 1}/{MAX_RESTARTS})")
                    runner.restart_count += 1
                    runner.restart()
                else:
                    logger.error(f"Maximum restart attempts ({MAX_RESTARTS}) reached. Exiting.")
                    break
                    
            # Check if we've been running too long and should restart for freshness
            current_time = time.time()
            if current_time - runner.start_time > MAX_RUNTIME:
                logger.info(f"Service has been running for {MAX_RUNTIME/3600} hours. Restarting for freshness.")
                runner.restart_count = 0  # Reset counter for scheduled restarts
                runner.start_time = current_time
                runner.restart()
                
    except Exception as e:
        logger.error(f"Error in service runner: {e}")
        runner.stop()
