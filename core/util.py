#!/usr/bin/env python
from pathlib import Path
import re

current_dir = Path(__file__).resolve().parent.parent
config_dir = Path(f"{current_dir}/config/")
TARGET_PORT = ":1080"

CONFIG_NAME_RE = re.compile(r"[a-zA-Z0-9_-]+")


class InvalidConfigName(ValueError):
  pass


def valid_config_name(name):
  return isinstance(name, str) and CONFIG_NAME_RE.fullmatch(name) is not None


def config_path(name):
  if not valid_config_name(name):
    raise InvalidConfigName(name)
  path = config_dir.joinpath(name)
  try:
    path.resolve().relative_to(config_dir.resolve())
  except ValueError:
    raise InvalidConfigName(name)
  return path
