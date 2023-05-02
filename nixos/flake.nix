{
  description = "Env Sensor Flake";

  inputs = {
	nixpkgs.url = github:NixOS/nixpkgs/nixos-22.11;
  };

  outputs = { 
    self
    , nixpkgs
    , ... }@inputs:
  with inputs.nixpkgs.lib;
  let
    config = {
      allowUnfree = true;
    };
    pkgs = {
	nixpkgs = { inherit config; };
    };
  in
  {
    nixosConfigurations = {
      envsensor = nixosSystem {
        system = "x86_64-linux";
	modules = [
	  ./conf
	  pkgs
	];
      };
    };
  };
}
