{
  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-23.05";
    systems.url = "github:nix-systems/default";
    devenv.url = "github:cachix/devenv";
    nixpkgs-python.url = "github:cachix/nixpkgs-python";
  };

  nixConfig = {
    extra-trusted-public-keys = "devenv.cachix.org-1:w1cLUi8dv3hnoSPGAuibQv+f9TZLr6cv/Hm9XgU50cw=";
    extra-substituters = "https://devenv.cachix.org";
  };

  outputs = {
    self,
    nixpkgs,
    devenv,
    systems,
    ...
  } @ inputs: let
    forEachSystem = nixpkgs.lib.genAttrs (import systems);
  in {
    packages = forEachSystem (system: {
      devenv-up = self.devShells.${system}.default.config.procfileScript;
    });

    devShells =
      forEachSystem
      (system: let
        #pkgs = nixpkgs.legacyPackages.${system};
        pkgs = import nixpkgs {inherit system;};
      in {
        default = devenv.lib.mkShell {
          inherit inputs pkgs;
          modules = [
            {
              # https://devenv.sh/reference/options/
              packages = [
                pkgs.cowsay
                pkgs.lolcat
                #pkgs.uv
              ];

              enterShell = ''
                cowsay -p "Welcome to the devshell!" | lolcat
              '';

              languages.python.enable = true;
              languages.python.version = "3.12.1";

              pre-commit.hooks = {
                alejandra.enable = true;
                ruff.enable = true;
              };
            }
          ];
        };
      });
  };
}
