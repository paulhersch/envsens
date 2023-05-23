# vim:expandtab ts=2 sw=2
{ config, pkgs, ... }:

{
  imports =
    [
      ./hardware-configuration.nix
    ];

  nix = {
    settings = {
      auto-optimise-store = true;
      # activate flakes
      experimental-features = [ "nix-command" "flakes" ];
    };
    # keeps built derivations in gc
    extraOptions = ''
      keep-outputs = true
    '';
  };

  boot.loader = {
  systemd-boot.enable = true;
    efi = {
      canTouchEfiVariables = true;
      efiSysMountPoint = "/boot/EFI";
    };
  };
  
  services.envsens.enable = true;

  networking.hostName = "envsens-server";
  networking.networkmanager.enable = true;

  time.timeZone = "Europe/Berlin";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  i18n.defaultLocale = "de_DE.UTF-8";
  console = {
    keyMap = "de-latin1";
  };

  # "admin" account (for ssh in case this is needed)
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ ];
  };

  environment.systemPackages = with pkgs; [
    neovim
    git
    sqlite
  ];

  networking.firewall = {
    enable = true;
    allowedTCPPorts = [ 8888 ]; 
  };

  system.stateVersion = "22.11";
}
