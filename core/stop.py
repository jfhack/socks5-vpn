#!/usr/bin/env python
from core import util, db
import subprocess

class Stop:
  def __init__(self, name, force=False):
    self.name = name
    self.config_dir = util.config_dir.joinpath(self.name)
    if self.config_dir.exists():
      self.stop(force)
    else:
      print(f"ERROR: {self.name} does not exist")
      exit(1)

  def stop(self, force=False):
    self.db = db.DBCounter(self.config_dir.joinpath("counter.db"))
    if force:
      self.db.reset()
      subprocess.run(["docker", "compose", "down", "-v"], cwd=self.config_dir)
      print(f"Stopped {self.name}")
      return
    self.db.decrease()
    if self.db.get_count() == 0:
      subprocess.run(["docker", "compose", "down", "-v"], cwd=self.config_dir)
      print(f"Stopped {self.name}")
    else:
      print(f"Stopped {self.name} (but not really)")
