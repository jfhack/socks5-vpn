#!/usr/bin/env python
from tabulate import tabulate
from core import util, db

class List:
  def __init__(self):
    print(self.ls())

  def ls(self):
    table = []
    for file in util.config_dir.iterdir():
      if file.is_dir():
        active = db.DBCounter(file.joinpath("counter.db")).get_count()
        table.append((file.name, active))
    return tabulate(table, ["Name", "Active"], tablefmt="plain")
  

