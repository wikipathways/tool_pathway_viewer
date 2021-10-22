{ hostPkgs ? import <nixpkgs> {}, stdenv ? hostPkgs.stdenv }:
let
  # overlayed nixpkgs
  pkgs = import (builtins.fetchTarball {
    name = "nixos-unstable-2021-10-12";
    # url obtained by looking up latest commit hash at https://github.com/nixos/nixpkgs
    url = "https://github.com/nixos/nixpkgs/archive/cd53bf7accfde9fe2d2232a73cf85813752a15cd.tar.gz";
    # sha256 hash obtained using `nix-prefetch-url --unpack <url>`
    sha256 = "1vlnf0bbky1h0yc8zbl3l2nmnzx37a0v83bfpx1hwrsr6cdqwzs4";
  }) { config.allowUnfree = true; };
in
pkgs.mkShell {
  buildInputs = with pkgs; [
    # for python
    python3
    # python3.pkgs.django still at v2 as of 2021-10-12 
    python3.pkgs.django_3
    python3.pkgs.requests
    python3.pkgs.webcolors
  ] ++ (if stdenv.isDarwin then [

    # more node-gyp dependencies

    # XCode Command Line Tools
    # TODO: do we need cctools?
    pkgs.darwin.cctools

  ] else [

    # more node-gyp dependencies
    pkgs.gnumake

    # gcc and binutils disagree on the version of a
    # dependency, so we need to binutils-unwrapped.
    pkgs.gcc # also provides cc
    pkgs.binutils-unwrapped # provides ar

  ]) ++ [

  ];
}
