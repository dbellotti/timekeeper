{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    flake-utils.url = "github:numtide/flake-utils";
    flake-utils.inputs.nixpkgs.follows = "nixpkgs";
  };
  outputs = { self, nixpkgs, flake-utils }:
    flake-utils.lib.eachDefaultSystem
      (system:
        let
          pkgs = import nixpkgs { inherit system; };
        in
        with pkgs;
        {
          devShells.default = mkShell {
            packages = [
              # adds python3.12 and packages
              (python312.withPackages (python-pkgs: [
                # You can add python packages here
                # python-pkgs.pytest
              ]))

              mypy
              ruff
            ];
          };
        }
      );
}
