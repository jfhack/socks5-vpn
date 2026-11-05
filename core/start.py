#!/usr/bin/env python
from core import util, db
import subprocess
import yaml
import time

class Start:
  def __init__(self, name):
    self.name = name
    self.config_dir = util.config_path(self.name)

    if self.config_dir.exists():
      self.start()
    else:
      print(f"ERROR: {self.name} does not exist")
      exit(1)

  def start(self):
    self.db = db.DBCounter(self.config_dir.joinpath("counter.db"))
    self.db.increase()
    subprocess.run(["docker", "compose", "up", "-d"], cwd=self.config_dir)
    print(f"Started {self.name}")
    config = self.get_config()
    time.sleep(config.get("start_delay", 2))

  def get_config(self):
    config = None
    try:
      with open(self.config_dir.joinpath("config.yml"), 'r') as config_file:
        config = yaml.safe_load(config_file)
    except (OSError, yaml.YAMLError):
      pass
    return config if isinstance(config, dict) else dict()

