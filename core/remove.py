#!/usr/bin/env python
from core import util, db
from core.stop import Stop
import shutil

class Remove:
  def __init__(self, name):
    self.name = name
    self.config_dir = util.config_dir.joinpath(self.name)
    self.remove()

  def remove(self):
    self.db = db.DBCounter(self.config_dir.joinpath("counter.db"))
    if self.db.get_count() != 0:
      action = input(f"WARNING: {self.name} is still running. It is recommended to stop it first. Do you want to continue? It will stop and remove it (y/n) ")
      if action == "y":
        Stop(self.name, force=True)
      else:
        return
    shutil.rmtree(self.config_dir)
    print(f"Removed {self.name}")