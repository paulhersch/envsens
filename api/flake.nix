{
    description = "Flake for API of Prototyping Project for a low energy environment sensor";
    
    inputs = {
        # "stable" package set
        nixpkgs.url = github:NixOS/nixpkgs/nixos-22.11;
    };
    
    outputs = {
        self
        , nixpkgs
        , ...
    }@inputs:
    let
        system = "x86_64-linux";
        pkgs = nixpkgs.legacyPackages.${system};
        py_run_deps = (p: with p; [
            fastapi
            uvicorn
            aiosqlite
        ]);
    in 
    with pkgs;
    {
        devShells.${system}.default = pkgs.mkShell {
            nativeBuildInputs = with pkgs; [
                # dev programs
                sqlite
                (pkgs.python3.withPackages (ps: with ps; [
                    # dev libs
                    requests
                ] ++ (py_run_deps ps)))
            ];
        };
        packages.${system}.default = pkgs.python3Packages.buildPythonPackage {
            pname = "envsens-api";
            version = "0.0.1rc1";
            src = ./.;    
            doCheck = false;
            propagatedBuildInputs = with pkgs.python3Packages; [
                uvicorn
                fastapi
                aiosqlite
            ];
            nativeBuildInputs = with pkgs.python3Packages; [ setuptools-scm ];
        };
        nixosModules.apiservice = { config, lib, ... }: 
            with lib;
            let
                cfg = config.services.envsens;
            in
            {
                options.services.envsens = {
                    enable = mkEnableOption "Enable the envsens API service";
                };

                config = mkIf cfg.enable {
                    systemd.services."envsens" = {
                        enable = true;
                        description = "Envsens API with ML prediction model";
                        wantedBy = [ "network.target" ];
                        environment = {
                            DB_PATH="/var/lib/envsens/db.sqlite";
                            TOKEN_PATH="/var/lib/envsens/token";
                        };
                        serviceConfig = {
                            ExecStart = "${self.packages.${system}.default}/bin/envsens-api --port 8888";
                            Restart = "on-failure";
                            RestartSec = 5;
                        };
                        preStart = ''
                            [[ ! -d /var/lib/envsens ]] && mkdir -p /var/lib/envsens || exit 0
                        '';
                    };
                };
            };
    };
}
