let
  nixpkgs = fetchTarball "https://github.com/NixOS/nixpkgs/tarball/nixos-22.11";
  pkgs = import nixpkgs { config = {}; overlays = []; };
in 
{
  hello = pkgs.callPackage ./hello.nix {};
  icat = pkgs.callPackage ./icat.nix {};
}
