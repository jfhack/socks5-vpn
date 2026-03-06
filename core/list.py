#!/usr/bin/env python
from tabulate import tabulate
from core import util, db
from core.get import Get

class List:
  def __init__(self, args):
    self.args = args
    print(self.ls())

  def ls(self):
    table = []
    colnames = ["Name", "Active"]
    if self.args.port:
      colnames.append("Port")
    for file in util.config_dir.iterdir():
      if file.is_dir():
        active = db.DBCounter(file.joinpath("counter.db")).get_count()
        row = [file.name, active]
        if self.args.port:
          port = ""
          try:
            port = Get(file.name, self.args, show=False).get_port()
          except Exception as e:
            pass
          row.append(port)
        table.append(row)
    return tabulate(table, colnames, tablefmt="plain")
  

