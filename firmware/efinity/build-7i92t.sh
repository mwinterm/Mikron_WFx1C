#!/bin/bash
# build-7i92t.sh -- builds 7i92t_7i77_7i74DP.bin, the probe firmware for a
# 7I92T/7I92TH (Efinix Trion T20F256), from Mesa's sources and the PIN file
# beside this directory:
#
#   1. a fresh copy of Mesa's sources in $WORK/hm2: 7i92t.zip (sha256
#      checked) -> configs/hostmot2/source/7i92t-hm2.zip
#   2. ../PIN_7I77_7I74DP_34.vhd beside the other PIN files
#   3. TopEthernet16HostMot2_efx.vhd: its one active `use work.PIN_...` line
#      replaced by the probe file's
#   4. seveni92t.xml: the PIN file added to the design, the place-and-route
#      seed set (SEED, 2 by default: Mesa's note for PIN_7I77_7I74D_34)
#   5. efx_run.py seveni92t.xml --prj --flow compile; the bitstream to $OUT
#      with its sha256, every report in $WORK/logs/build-<time>/
#
# MESA_ZIP names Mesa's 7i92t.zip (mesanet.com, software/parallel/), EFINITY
# the unpacked Efinity installation (the directory holding bin/setup.sh).
# --prepare-only stops after step 4 and needs no Efinity. In the container
# the Dockerfile here builds, with the repository, the zip and Efinity
# mounted at the same paths as outside:
#
#   docker build -t efinity firmware/efinity
#   docker run --rm --user "$(id -u):$(id -g)" -e HOME=/tmp \
#     -e MESA_ZIP=$MESA_ZIP -e EFINITY=$EFINITY \
#     -v "$PWD:$PWD" -v "$MESA_ZIP:$MESA_ZIP:ro" -v "$EFINITY:$EFINITY:ro" \
#     -w "$PWD" efinity firmware/efinity/build-7i92t.sh
set -euo pipefail
PREPARE_ONLY=0
[ "${1:-}" = "--prepare-only" ] && PREPARE_ONLY=1
HERE=$(cd "$(dirname "$0")" && pwd)
FW=$(dirname "$HERE")
WORK=${WORK:-$HERE/work}
W=$WORK/hm2
ZIP=${MESA_ZIP:?MESA_ZIP must name the 7i92t.zip from Mesa}
ZIP_SHA=${ZIP_SHA:-7641bd9db502044259699afedc1ebca24c7d19e38dc1d23afbac01c6239feed9}
PIN=$FW/PIN_7I77_7I74DP_34.vhd
OUT=${OUT:-$WORK/7i92t_7i77_7i74DP.bin}
SEED=${SEED:-2}
L=$WORK/logs/$([ "$PREPARE_ONLY" = 1 ] && echo prepare || echo build)-$(date +%Y%m%d-%H%M%S)

if [ "$PREPARE_ONLY" = 0 ]; then
  [ -f "${EFINITY:-}/bin/setup.sh" ] || { echo "EFINITY must name the Efinity installation (the directory with bin/setup.sh)" >&2; exit 1; }
fi
echo "$ZIP_SHA  $ZIP" | sha256sum -c --quiet

# 1-2: the sources, from scratch every time.
rm -rf "$W" "$WORK/zip"
mkdir -p "$WORK/zip" "$W" "$L"
unzip -q "$ZIP" '7i92t/configs/hostmot2/source/7i92t-hm2.zip' -d "$WORK/zip"
unzip -q "$WORK/zip/7i92t/configs/hostmot2/source/7i92t-hm2.zip" -d "$W"
cp "$PIN" "$W/PIN_7I77_7I74DP_34.vhd"

# 3: the top file uses the probe PIN file, and only it.
T=$W/TopEthernet16HostMot2_efx.vhd
active=$(grep -c '^use work\.PIN_' "$T")
[ "$active" = 1 ] || { echo "$T has $active active PIN lines, not 1" >&2; exit 1; }
sed -i 's/^use work\.PIN_.*/use work.PIN_7I77_7I74DP_34.all;  -- Mikron_WFx1C: the probe on I\/O 16/' "$T"
grep -q '^use work\.i92t_x20card\.all;' "$T" || { echo "$T does not use i92t_x20card" >&2; exit 1; }

# 4: the project knows the file and the seed.
P=$W/seveni92t.xml
grep -q 'name="PIN_7I77_7I74D_34.vhd"' "$P" || { echo "$P has no PIN_7I77_7I74D_34.vhd to add beside" >&2; exit 1; }
sed -i 's|\( *\)<efx:design_file name="PIN_7I77_7I74D_34.vhd"\(.*\)|&\n\1<efx:design_file name="PIN_7I77_7I74DP_34.vhd"\2|' "$P"
grep -q '<efx:param name="seed" value="[0-9]*"' "$P" || { echo "$P has no seed" >&2; exit 1; }
sed -i "s|<efx:param name=\"seed\" value=\"[0-9]*\"|<efx:param name=\"seed\" value=\"$SEED\"|" "$P"
cp "$T" "$P" "$L/"
echo "prepared $W: PIN_7I77_7I74DP_34, seed $SEED"
[ "$PREPARE_ONLY" = 1 ] && exit 0

# 5: the flow, headless.
cd "$W"
# setup.sh is not written for -e and -u.
set +eu
# shellcheck disable=SC1091
source "$EFINITY/bin/setup.sh"
set -eu
efx_run.py seveni92t.xml --prj --flow compile 2>&1 | tee "$L/efx_run.log"
cp -r outflow "$L/" 2>/dev/null || true
# Without the Interface Designer's constraints efx_pgm writes no bitstream
# and every stage still says PASS (libsqlite3 missing did that once).
if grep -q 'Skipping Interface Designer step' outflow/seveni92t.log; then
  echo "the Interface Designer step was skipped: see $L/outflow/seveni92t.log" >&2; exit 1
fi
bin=$(ls outflow/seveni92t.hex.bin outflow/seveni92t.bin 2>/dev/null | head -1 || true)
[ -n "$bin" ] || { echo "no bitstream in outflow: see $L" >&2; exit 1; }
mkdir -p "$(dirname "$OUT")"
cp "$bin" "$OUT"
(cd "$(dirname "$OUT")" && sha256sum "$(basename "$OUT")" > "$(basename "$OUT").sha256")
grep -A2 'Setup (Max) Clock Relationship' outflow/seveni92t.timing.rpt | tail -1
echo "built $OUT ($(cut -c1-16 "$OUT.sha256")...)"
