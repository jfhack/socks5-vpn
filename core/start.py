#!/usr/bin/env python
from core import util, db
import subprocess
import yaml
import time

class Start:
  def __init__(self, name):
    self.name = name
    self.config_dir = util.config_dir.joinpath(self.name)

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
    config = dict()
    try:
      with open(self.config_dir.joinpath("config.yml"), 'w') as config_file:
        config = yaml.safe_load(config_file)
    except:
      pass
    return config

