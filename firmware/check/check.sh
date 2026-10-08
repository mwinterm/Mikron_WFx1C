#!/bin/sh
# Runs the PIN file's derived constants through GHDL in a throwaway Debian
# container: which I/O is the probe input, which channel pairs keep their
# index, how many smart-serial channels each port has, and the version the
# muxed encoder module reports.
#
# Usage: check/check.sh <unpacked hostmot2 source directory>
set -eu
src=$(cd "$1" && pwd)
here=$(cd "$(dirname "$0")/.." && pwd)
docker run --rm -v "$src":/src:ro -v "$here":/fw:ro debian:13 sh -c '
  apt-get update -qq >/dev/null && apt-get install -y -qq ghdl >/dev/null 2>&1
  mkdir /w && cd /w
  o="--std=93c -fsynopsys -fexplicit"
  for f in /src/IDROMConst.vhd /fw/PIN_7I77_7I74DP_34.vhd \
           /src/InputPinsPerModule.vhd /fw/check/pin_check.vhd; do
    ghdl -a $o "$f" || exit 1
  done
  ghdl -e $o pin_check && ghdl -r $o pin_check 2>&1 | grep "report note"
'
