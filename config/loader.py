import yaml
import json
import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file if present (for local dev; Docker sets env vars directly)
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
TARGETS_PATH = BASE_DIR / "config" / "targets.json"

def load_config() -> dict:
    """Load config from YAML, with environment variable overrides."""
    config = {}
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            config = yaml.safe_load(f) or {}

    # Environment overrides take precedence over config.yaml
    if os.environ.get("TOR_PROXY_URL"):
        config.setdefault("crawler", {})["proxy"] = os.environ["TOR_PROXY_URL"]

    # API keys from environment (preferred) or config.yaml (fallback)
    apis = config.setdefault("apis", {})
    apis["abuseipdb"] = os.environ.get("ABUSEIPDB_API_KEY", apis.get("abuseipdb", ""))
    apis["virustotal"] = os.environ.get("VIRUSTOTAL_API_KEY", apis.get("virustotal", ""))
    apis["ipinfo"] = os.environ.get("IPINFO_API_KEY", apis.get("ipinfo", ""))

    return config

def load_targets() -> list:
    if TARGETS_PATH.exists():
        with open(TARGETS_PATH, "r") as f:
            data = json.load(f)
            return data.get("targets", [])
    return []

def save_targets(targets: list):
    with open(TARGETS_PATH, "w") as f:
        json.dump({"targets": targets}, f, indent=2)
