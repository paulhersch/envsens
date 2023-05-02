# What is this?
These are basic configuration files used by the server to run the API and serve the web app for our Energy Sensor.

The API is meant to be used by the ESP to send current data and give the web app the ability to
retrieve current data and predictions from the server

# Usage
## Installation
You need to clone this git repo to have access to the configuration files. I recommend to directly
clone to `/etc` to make management of the files easier.
```shell
git clone https://github.com/paulhersch/envsens /etc/envsensrepo
```
I then recommend symlinking this directory to the `/etc/nixos` directory on the target machine:
```shell
ln -s /etc/envsensrepo/nixos /etc/nixos
```
If you are installing the config on Your server, you need to specify the target
flake to use for the installation. After that `nixos-rebuild` will just pick the config
based on the hostname
```shell
nixos-install --flake .#envsensor 
```

## Testing in Container
If You are running NixOS you can also just test the servers config on your own machine
by running the config as NixOS container (needs to be run as root):
```shell
nixos-container create envsens --flake .#container
```
the container is then saved on your system with the name `envsens` and can be started
via `nixos-container`:
```shell
nixos-container start envsens
```
