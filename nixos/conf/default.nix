# vim:set tabstop=2:set shiftwidth=2:set expandtab
{ config, pkgs, ... }:

{
  imports =
    [
      ./hardware-configuration.nix
    ];

  nix = {
    # activate flakes
    settings = {
      auto-optimise-store = true;
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

  networking.hostName = "envsensor";
  networking.networkmanager.enable = true;

  time.timeZone = "Europe/Berlin";

  # Configure network proxy if necessary
  # networking.proxy.default = "http://user:password@proxy:port/";
  # networking.proxy.noProxy = "127.0.0.1,localhost,internal.domain";

  i18n.defaultLocale = "de_DE.UTF-8";
  console = {
    keyMap = "de-latin1";
  };

  # basic admin account
  users.users.alice = {
    isNormalUser = true;
    extraGroups = [ ]; # Enable ‘sudo’ for the user.
  };

  environment.systemPackages = with pkgs; [
    neovim
    git
  ];

  services.openssh.enable = true;

  # Open ports in the firewall.
  # networking.firewall.allowedTCPPorts = [ ... ];
  # networking.firewall.allowedUDPPorts = [ ... ];
  networking.firewall.enable = true;

  system.stateVersion = "22.11";
}
