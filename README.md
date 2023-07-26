# SOCKS5 VPN

This is a simple Python script that creates a SOCKS5 proxy over a VPN connection using Docker

It uses [dperson/openvpn-client](https://github.com/dperson/openvpn-client) and [serjs/socks5-server](https://github.com/serjs/socks5-server) as a base

This script is useful, for instance, when you want to browse over a VPN but don't want to subject your entire system to that VPN. In this scenario, you could use a browser with SOCKS5

## Usage

### Installation
First, install the necessary requirements

```sh
pip install -r requirements.txt
```

Now, you can execute the script `./socks5-vpn`

### Arguments

| Command | Argument | Description |
|-|-|-|
|create, new||create a VPN configuration|
||name|the name of the VPN configuration|
|start||start a VPN configuration|
||name|the name of the VPN configuration|
|stop||stop a VPN configuration|
||name|the name of the VPN configuration|
||-f, --force|force stop, even if other instances are still using the VPN|
|remove, rm||remove a VPN configuration|
||name|the name of the VPN configuration|
|get||get a VPN configuration|
||name|the name of the VPN configuration|
||-p, --port|get the port (full address:port if it was configured in this way) of the VPN configuration|
||-n, --port-number|get the port number of the VPN configuration|
|list, ls||list configurations|
|install||put a symbolic link of this script into a writable PATH directory|

### Creating a Configuration

To use this, it's required to create a VPN configuration, which can be done using the `create` command and providing the name as an argument. The name should not contain spaces or special symbols different from - or _. It can use alphanumeric characters.

Example:

```sh
./socks5-vpn create ru1050
```
```
Created ru1050 directory
Docker subnet [10.5.2.0/24]: 
Docker gateway [10.5.2.1]: 
Docker IP [10.5.2.5]: 
Socks5 port, as Docker port mapping
Examples:
  1080
  0.0.0.0:1080
  127.0.0.1:1080
You will use this port to connect to the socks5 proxy
Socks5 port [127.0.0.1:1080]: 127.0.0.1:7500
Do you want to use user and password for this proxy? [y/N]: 
No user and password will be used

Delay in seconds after the VPN started
The delay is useful to make systems running immediately after the 'start' command already have the VPN active or at least with time gained
Delay in seconds after the VPN started [2]: 

Created config/ru1050/docker-compose.yml

You need to add your *.ovpn or *.conf, and vpn.auth files into config/ru1050/vpn
Your vpn.auth file should contain your VPN username and password, separated by a newline

Done!
```

Once you've configured, you can copy, for example, your .ovpn file into `config/ru1050/vpn/`, and also include your credentials in a file named vpn.auth, thereby creating a structure like:


- config/ru1050/vpn/
  - ru1050.vpn
  - vpn.auth


The `vpn.auth` file might contain something like:
```
KuNezPeQifRu2bo9b4eY8GDU
Bf1klHXbvDYzV82iC7bWpX1v
```
For instance, these are typical credentials in the manual configuration of [NordVPN](https://nordvpn.com/), where the username and password are separated by a newline

### Install in PATH

It's recommended to install this in a PATH, so it's accessible from anywhere. You can do this with the following command:

```sh
./socks5-vpn install
```

You will get something like:

```
  Index  Path                                              Installed
      1  /home/lasker/.local/bin                             
      2  /home/lasker/go/bin
      3  /home/lasker/.cargo/bin
      4  /home/lasker/.pyenv/libexec
      5  /home/lasker/.pyenv/plugins/pyenv-virtualenv/shims
      6  /home/lasker/.pyenv/bin
      7  /home/lasker/.pyenv/plugins/python-build/bin
Select path to install to [1]:
Installed to /home/lasker/.local/bin

You can now run the script from anywhere by typing:
socks5-vpn
```

### Control

To start this example, you could run the following commands:
```sh
socks5-vpn start ru1050
# do something with the SOCK5 proxy
socks5-vpn stop ru1050
```

And you can list the configurations with:
```sh
socks5-vpn list
```
```
Name      Active
ru1050         0
```

Where `Active` is the number of times that the `start` command was called for that configuration, `stop` does the opposite, once the counter reaches zero it will turn down the Docker containers

### Example script

For instance, to use this with Chromium with Flatpak, you could create a script like this:

```sh
#!/bin/bash

vpn_name=$1
shift

port=$(socks5-vpn get $vpn_name -n)

socks5-vpn start $vpn_name

flatpak 'run' '--command=/app/bin/chromium' 'org.chromium.Chromium' "--user-data-dir=/home/lasker/.local/share/chromium-vavilov-$vpn_name/" --proxy-server="socks5://localhost:$port" "$@"

socks5-vpn stop $vpn_name
```

This script could be invoked as `./chromium-vavilov ru1050`

Enjoy!

This script has been tested on Ubuntu-based distributions