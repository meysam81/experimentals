let
  pkgs = import <nixpkgs> {};
in 
rec {
  hello = pkgs.callPackage ./hello.nix { audience = "people"; };
  hello-folks = hello.override { audience = "folks"; };
}

