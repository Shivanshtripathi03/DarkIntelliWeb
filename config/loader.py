import yaml
import json
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
CONFIG_PATH = BASE_DIR / "config" / "config.yaml"
TARGETS_PATH = BASE_DIR / "config" / "targets.json"

def load_config() -> dict:
    if CONFIG_PATH.exists():
        with open(CONFIG_PATH, "r") as f:
            return yaml.safe_load(f)
    return {}

def load_targets() -> list:
    if TARGETS_PATH.exists():
        with open(TARGETS_PATH, "r") as f:
            data = json.load(f)
            return data.get("targets", [])
    return []

def save_targets(targets: list):
    with open(TARGETS_PATH, "w") as f:
        json.dump({"targets": targets}, f, indent=2)
