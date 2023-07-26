#!/usr/bin/env python
from pathlib import Path
import re
import yaml
import ipaddress
from core import util

class Create:
  def __init__(self, name):
    self.name = name
    if not self.valid_config_name(name):
      print("Error: Invalid name")
      print("Valid characters are: a-z, A-Z, 0-9, _ and -")
      print("It will be used as the name of the directory and part of the Docker container name")
      exit(1)
    self.create_directory()
    self.create_config()

  def valid_config_name(self, name):
    return re.match(r"^[a-zA-Z0-9_-]+$", name)
  
  def create_directory(self):
    util.config_dir.mkdir(parents=True, exist_ok=True)
    if exist := util.config_dir.joinpath(self.name).exists():
      print(f"Warning: {self.name} already exists")

    util.config_dir.joinpath(self.name).mkdir(parents=True, exist_ok=True)
    if not exist:
      print(f"Created {self.name} directory")
    
    self.config_dir = util.config_dir.joinpath(self.name)

  def get_network(self, cidr):
    gateway = None
    for i, ip in enumerate(ipaddress.IPv4Network(cidr, strict=False)):
      if i == 1:
        gateway = str(ip)
      elif i == 5:
        break
    return gateway, str(ip)
  
  def get_other_configs(self):
    configs = dict()
    for config in util.config_dir.iterdir():
      if config.is_dir() and config.name != self.name:
        with open(config.joinpath("docker-compose.yml"), 'r') as config_file:
          configs[config.name] = yaml.safe_load(config_file)
    self.configs = configs

  def overlaps_other_cidr(self, cidr):
    for config_name, config in self.configs.items():
      subnet = ipaddress.IPv4Network(config['networks']['network']['ipam']['config'][0]['subnet'], strict=False)
      if subnet.overlaps(ipaddress.IPv4Network(cidr, strict=False)):
        return config_name

  def overlaps_other_port(self, port):
    clean = lambda p: p.replace("0.0.0.0", '').strip(':')
    result = []
    for config_name, config in self.configs.items():
      for config_port in config['services']['vpn']['ports']:
        config_port = clean(config_port[: -len(util.TARGET_PORT)])
        if port == config_port:
          result.append(config_name)
    return result

  def suggest_cidr(self, cidr):
    subnet = ipaddress.IPv4Network(cidr, strict=False)
    if not self.overlaps_other_cidr(str(subnet)):
      return str(subnet)
    for i in range(255):
      subnet = ipaddress.IPv4Network((subnet.network_address + subnet.num_addresses, subnet.prefixlen), strict=False)
      if not self.overlaps_other_cidr(str(subnet)):
        return str(subnet)
    return cidr

  def create_config(self):
    self.get_other_configs()
    with open(util.current_dir.joinpath("base.yml"), 'r') as base_file:
      self.base = yaml.safe_load(base_file)
      self.base['name'] = self.name
      self.base['services']['vpn']['container_name'] = f"{self.base['services']['vpn']['container_name']}-{self.name}"
      self.base['services']['socks5']['container_name'] = f"{self.base['services']['socks5']['container_name']}-{self.name}"
      default_cidr = self.base['networks']['network']['ipam']['config'][0]['subnet']
      default_cidr = self.suggest_cidr(default_cidr)
      while True:
        default_cidr = input(f"Docker subnet [{default_cidr}]: ") or default_cidr
        if re.match(r"^\d+\.\d+\.\d+\.\d+\/\d+$", default_cidr) and not (overlaps := self.overlaps_other_cidr(default_cidr)):
          break
        else:
          print("Invalid Docker subnet")
          if overlaps:
            print(f"Overlaps with {overlaps}")
      default_gateway, default_ip = self.get_network(default_cidr)
      while True:
        default_gateway = input(f"Docker gateway [{default_gateway}]: ") or default_gateway
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", default_gateway):
          break
        else:
          print("Invalid Docker gateway")
      while True:
        default_ip = input(f"Docker IP [{default_ip}]: ") or default_ip
        if re.match(r"^\d+\.\d+\.\d+\.\d+$", default_ip):
          break
        else:
          print("Invalid Docker IP")
      self.base['networks']['network']['ipam']['config'][0]['subnet'] = default_cidr
      self.base['networks']['network']['ipam']['config'][0]['gateway'] = default_gateway
      self.base['services']['vpn']['networks']['network']['ipv4_address'] = default_ip

      
      for i, port in enumerate(self.base['services']['vpn']['ports']):
        if port.endswith(util.TARGET_PORT):
          default_port = port[: -len(util.TARGET_PORT)]
          print("Socks5 port, as Docker port mapping")
          print("Examples:")
          print("  1080")
          print("  0.0.0.0:1080")
          print("  127.0.0.1:1080")
          print("You will use this port to connect to the socks5 proxy")
          original_default_port = default_port
          while True:
            default_port = input(f"Socks5 port [{default_port}]: ") or default_port
            if re.match(r"^\d+\.\d+\.\d+\.\d+\:\d+$", default_port) or re.match(r"^[\:]*\d+$", default_port):
              if not (overlaps := self.overlaps_other_port(default_port)):
                break
              else:
                print(f"Overlaps with [{', '.join(overlaps)}]")
                print("This means that you will not be able to use this port in parallel with the other configurations")
                action = input("Do you want to use this port anyway? [y/N]: ").lower() or "n"
                if action == "y":
                  break
            else:
              print("Invalid Socks5 port")
              default_port = original_default_port

          self.base['services']['vpn']['ports'][i] = f"{default_port}{util.TARGET_PORT}"
          break
    action = input("Do you want to use user and password for this proxy? [y/N]: ").lower() or "n"
    if action == "y":
      proxy_user = input(f"Socks5 user: ")
      if proxy_user:
        print("Warning: The password will be visible typing here, and in the docker-compose.yml file")
        proxy_password = input(f"Socks5 password: ")
        self.base["services"]["socks5"]["environment"] = [f"PROXY_USER={proxy_user}", f"PROXY_PASSWORD={proxy_password}"]
      else:
        print("No user and password will be used")
    else:
      print("No user and password will be used")

    default_delay = "2"
    print("\nDelay in seconds after the VPN started")
    print("The delay is useful to make systems running immediately after the 'start' command already have the VPN active or at least with time gained")
    while True:
      try:
        default_delay = int(input(f"Delay in seconds after the VPN started [{default_delay}]: ") or default_delay)
        if default_delay >= 0:
          break
        else:
          print("Invalid delay")
      except ValueError:
        print("Invalid delay")
    config = dict(start_delay = default_delay)
    with open(self.config_dir.joinpath("config.yml"), 'w') as config_file:
      yaml.dump(config, config_file, default_flow_style=False)

    with open(self.config_dir.joinpath("docker-compose.yml"), 'w') as config_file:
      yaml.dump(self.base, config_file, default_flow_style=False)
    print(f"\nCreated config/{self.name}/docker-compose.yml")
    self.config_dir.joinpath("vpn").mkdir(parents=True, exist_ok=True)
    print(f"\nYou need to add your *.ovpn or *.conf, and vpn.auth files into config/{self.name}/vpn")
    print("Your vpn.auth file should contain your VPN username and password, separated by a newline")
    print("\nDone!")

