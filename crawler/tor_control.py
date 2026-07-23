import os
from stem import Signal
from stem.control import Controller
from config.logger import setup_logger

logger = setup_logger("tor_control")

TOR_CONTROL_HOST = os.environ.get("TOR_CONTROL_HOST", "localhost")
TOR_CONTROL_PORT = int(os.environ.get("TOR_CONTROL_PORT", 9051))


def rotate_circuit():
    """Request a new Tor circuit (NEWNYM signal).
    
    This forces Tor to build a new circuit for subsequent connections,
    effectively changing the exit node IP. Rate-limited by Tor to once
    every ~10 seconds.
    """
    try:
        with Controller.from_port(address=TOR_CONTROL_HOST, port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()
            controller.signal(Signal.NEWNYM)
            logger.info("Tor circuit rotated successfully (NEWNYM).")
            return True
    except Exception as e:
        logger.error(f"Failed to rotate Tor circuit: {e}")
        return False


def get_tor_status() -> dict:
    """Check Tor connectivity and return status info."""
    try:
        with Controller.from_port(address=TOR_CONTROL_HOST, port=TOR_CONTROL_PORT) as controller:
            controller.authenticate()
            version = str(controller.get_version())
            circuits = controller.get_circuits()
            return {
                "status": "connected",
                "version": version,
                "active_circuits": len(circuits)
            }
    except Exception as e:
        logger.error(f"Tor status check failed: {e}")
        return {"status": "disconnected", "error": str(e)}
