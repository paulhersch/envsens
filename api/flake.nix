{
    description = "Flake for API of Prototyping Project for a low energy environment sensor";
    
    inputs = {
        # "stable" package set
        nixpkgs.url = github:NixOS/nixpkgs/nixos-22.11;
        flake-utils.url = github:numtide/flake-utils;
    };
    
    outputs = {
        self
        , nixpkgs
        , flake-utils
    }@inputs:
    flake-utils.lib.eachDefaultSystem (system:
        let
            pkgs = nixpkgs.legacyPackages.${system};
            py_run_deps = (p: with p; [
                fastapi
                uvicorn
                aiosqlite
            ]);
        in 
        with pkgs;
        {
            devShell = pkgs.mkShell {
                nativeBuildInputs = with pkgs; [
                    sqlite
                    (pkgs.python3.withPackages (ps: with ps; [
                    ] ++ (py_run_deps ps)))
                ];
            };
            # packages.${system}.default = mkDerivation {
            #
            # };
        }
    );
}
