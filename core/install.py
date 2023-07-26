#!/usr/bin/env python
import os
from pathlib import Path
from tabulate import tabulate

class Install:
  def __init__(self, source):
    pathlist = os.environ.get("PATH").split(":")
    script_path = Path(source).resolve()
    writable = set()
    for path in pathlist:
      path = Path(path)
      if os.access(path, os.W_OK) and path.exists() and path.is_dir():
        writable.add(path)
    suggested_path = Path.home().joinpath(".local/bin")
    writable = list(writable)

    if len(writable) == 0:
      print("ERROR: No writable path found")
      print(f"Try run:\nsudo ln -s {script_path} /usr/local/bin")
      exit(1)

    writable.sort(key=lambda x: str(x) == str(suggested_path), reverse=True)
    table = []
    for i, path in enumerate(writable):
      installed = ""
      if path.joinpath(script_path.name).exists():
        installed = "Yes"
      table.append((i+1, path, installed))
    t = tabulate(table, ["Index", "Path", "Installed"], tablefmt="plain")
    print(t)
    path_index = "1"
    path_index = int(input(f"\nSelect path to install to [{path_index}]: ") or path_index)
    if path_index > len(writable) or path_index < 1:
      print("ERROR: Invalid index")
      exit(1)
    path = writable[path_index-1]
    if path.joinpath(script_path.name).exists():
      print("ERROR: Already installed")
      exit(1)
    os.symlink(script_path, path.joinpath(script_path.name))
    print(f"\nInstalled to {path.joinpath(script_path.name)}\n")
    print("You can now run the script from anywhere by typing:")
    print(f"{script_path.name}")
