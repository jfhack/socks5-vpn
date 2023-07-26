#!/usr/bin/env python
from tabulate import tabulate
from core import util, db
import yaml

class Get:
  def __init__(self, name, args):
    self.name = name
    self.args = args
    self.config_dir = util.config_dir.joinpath(self.name)

    if self.config_dir.exists():
      self.get()
    else:
      print(f"ERROR: {self.name} does not exist")
      exit(1)

  def get_all(self):
    table = []
    table.append(("port-address", self.get_port()))
    table.append(("port-number", self.get_port_number()))
    return tabulate(table, tablefmt="plain")

  
  def get_port(self):
    with open(self.config_dir.joinpath("docker-compose.yml"), 'r') as config_file:
      config = yaml.safe_load(config_file)
      for i, port in enumerate(config['services']['vpn']['ports']):
        if port.endswith(util.TARGET_PORT):
          return port[: -len(util.TARGET_PORT)]
    return ""
  
  def get_port_number(self):
    return self.get_port().split(":")[-1]

  def get(self):
    if self.args.port:
      print(self.get_port())
    elif self.args.port_number:
      print(self.get_port_number())
    else:
      print(self.get_all())