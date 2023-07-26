#!/usr/bin/env python
from pathlib import Path

current_dir = Path(__file__).resolve().parent.parent
config_dir = Path(f"{current_dir}/config/")
TARGET_PORT = ":1080"
