{
    description = "Flake for API of Prototyping Project for a low energy environment sensor";
    
    inputs = {
        # "unstable" package set
        nixpkgs.url = github:NixOS/nixpkgs/nixos-23.05;
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
            aiofiles
            scikit-learn
            keras
            tensorflow
            numpy
            pandas
        ]);
    in 
    with pkgs;
    {
        devShells.${system}.default = pkgs.mkShell {
            LD_LIBRARY_PATH="${pkgs.gcc-unwrapped}/lib64";
            nativeBuildInputs = with pkgs; [
                # dev programs
                sqlite
                libffi.dev
                (pkgs.python310.withPackages (ps: with ps; [
                    # dev libs
                    requests
                ] ++ (py_run_deps ps)
                ))
            ];
        };
        packages.${system}.default = pkgs.python310Packages.buildPythonPackage {
            pname = "envsens-api";
            version = "0.0.1rc1";
            src = ./.;    
            doCheck = false;
            propagatedBuildInputs = with pkgs.python310Packages; [
                uvicorn
                fastapi
                aiosqlite
		aiofiles
		scikit-learn
		keras
		tensorflow
		numpy
            ];
            nativeBuildInputs = with pkgs.python310Packages; [ setuptools-scm ];
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
                    users.groups.envsens = {};
                    users.users.envsens = {
                        name = "envsens";
                        group = "envsens";
                        description = "Envsens server user";
                        home = "/var/lib/envsens";
		        isSystemUser = true;
                    };
                    systemd.services."envsens" = {
                        enable = true;
                        description = "Envsens API with ML prediction model";
                        wantedBy = [ "network.target" ];
                        environment = {
                            DB_PATH="/var/lib/envsens/db.sqlite";
                            TOKEN_PATH="/var/lib/envsens/token";
                            MODEL_PATH="/var/lib/envsens/models";
                        };
                        serviceConfig = {
                            ExecStart = "${self.packages.${system}.default}/bin/envsens-api --port 6632";
                            Restart = "on-failure";
                            RestartSec = 5;
                            User = "envsens";
                            Group = "envsens";
                        };
                        preStart = ''
                            [[ ! -d /var/lib/envsens ]] && mkdir -p /var/lib/envsens
                            [[ ! -d /var/lib/envsens/models ]] && mkdir /var/lib/envsens/models || exit 0
                        '';
                    };
                };
            };
    };
}
