# vim:expandtab ts=2 sw=2
{
  description = "Env Sensor Flake";

  inputs = {
    nixpkgs.url = github:NixOS/nixpkgs/nixos-22.11;
    envsens.url = "./api";
  };

  outputs = { 
    self
    , nixpkgs
    , ... }@inputs:
  with inputs.nixpkgs.lib;
  let
    system = "x86_64-linux";
    config = {
      allowUnfree = true;
    };
    pkgs = {
      nixpkgs = {
        inherit config system;
      };
    };
  in
  {
    nixosConfigurations = {
      envsens-server = nixosSystem {
        system = "x86_64-linux";
	modules = [
          inputs.envsens.nixosModules.apiservice
          ./nixos
          pkgs
        ];
      };
      container = nixosSystem {
        modules = [
          inputs.envsens.nixosModules.apiservice
          ./nixos
          pkgs
          {
            boot.isContainer = true;
          }
        ];
      };
    };
  };
}
