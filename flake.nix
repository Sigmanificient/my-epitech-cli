{
  inputs = {
    nixpkgs.url = "nixpkgs/nixos-23.05";

    my-epitech-relay-git = {
      url = "github:norech/my-epitech-relay/master";
      flake = false;
    };
  };

  outputs = { nixpkgs, my-epitech-relay-git, ... }:
    let
      forAllSystems = function:
        nixpkgs.lib.genAttrs [
          "x86_64-linux"
          "aarch64-linux"
          "x86_64-darwin"
          "aarch64-darwin"
        ] (system: function nixpkgs.legacyPackages.${system});
    in {
      formatter = forAllSystems (pkgs: pkgs.nixpkgs-fmt);

      devShells = forAllSystems (pkgs: {
        default = pkgs.mkShell {
          packages = with pkgs; [
            python311
            nodejs
            chromium
          ];
        };
      });

      packages = forAllSystems (pkgs: rec {
        my-epitech-relay = pkgs.buildNpmPackage rec {
          name = "my-epitech-relay";
          version = "1.0.0";

          src = my-epitech-relay-git;
          npmDepsHash = "sha256-r6IBNmzBEhmo2/nUroYrlpRz9RwceL3nm9rzRWOwUaA=";

          buildInputs = with pkgs; [ nodejs_20 ];
          PUPPETEER_SKIP_DOWNLOAD = "true";

          installPhase = ''
            mkdir -p $out/bin

            npm run build

            cp out/index.js $out/index.js
            cp out/cookies.js $out/cookies.js

            cp -r node_modules $out/node_modules

            cat <<EOF > $out/bin/${name}
            #!${pkgs.runtimeShell}

            export BROWSER_BINARY_PATH=${pkgs.chromium}/bin/chromium
            ${pkgs.nodejs}/bin/node $out/index.js
            EOF

            chmod +x $out/bin/${name}
          '';
        };

        default = my-epitech-relay;
      });
    };
}
