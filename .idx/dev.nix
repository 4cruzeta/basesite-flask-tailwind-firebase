# To learn more about how to use Nix to configure your environment
# see: https://developers.google.com/idx/guides/customize-idx-env
{ pkgs, ... }: {
  # Which nixpkgs channel to use.
  channel = "stable-24.05"; # or "unstable"
  # Use https://search.nixos.org/packages to find packages
  packages = [
    pkgs.python313
    pkgs.uv
    pkgs.nodejs_22
    pkgs.gettext
  ];
  # Sets environment variables in the workspace
  env = {};
  idx = {
    # Search for the extensions you want on https://open-vsx.org/ and use "publisher.id"
    extensions = [
      # "vscodevim.vim"
      "google.gemini-cli-vscode-ide-companion"
    ];
    # Enable previews
    previews = {
      enable = true;
      previews = {
        web = {
          command = ["./devserver.sh"];
          env = {
            PORT = "$PORT";
          };
          manager = "web";
        };
      };
    };
    # Workspace lifecycle hooks
    workspace = {
      # Runs when a workspace is first created
      onCreate = {
        create-venv = ''
          python -m venv .venv
          source .venv/bin/activate
        '';
        # Example: install JS dependencies from NPM
        # npm-install = "npm install";
        # Open editors for the following files by default, if they exist:
        default.openFiles = [ ".idx/dev.nix" "README.md" ];
      };
      # Runs when the workspace is (re)started
      onStart = {
        # Example: start a background task to watch and re-build backend code
        # tailwind-watch = "cd basesite/ && python manage.py tailwind start";
        tailwind-watch = "npx @tailwindcss/cli -i ./edcat_root/static/css/input.css -o ./edcat_root/static/css/output.css --watch";
      };
    };
  };
}