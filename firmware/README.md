# 7i92t_7i77_7i74DP and 7i92_7i77_7i74DP: the WF41C's card with a probe input

The WF41C's Mesa card runs Mesa's stock `7i77_7i74D` layout: a 7I77 on one
connector (six muxed encoders, the analog outputs, field I/O) and a 7I74 on
the other (eight smart-serial channels). That firmware has no probe input,
so a touch probe can only be read once per servo cycle.

The card was a **7I92** (Xilinx Spartan-6 XC6SLX9) until it failed on
2026-10-11; a **7I92TH** (Efinix Trion T20F256) replaced it on 2026-10-13.
One PIN file serves both: built with ISE for the 7I92 as
`7i92_7i77_7i74DP.bit`, with Efinity for the 7I92T as
`7i92t_7i77_7i74DP.bin`, which the 7I92TH runs since 2026-10-14. hostmot2
names a 7I92T a 7I92, so the HAL names are `hm2_7i92.0` on either.

`PIN_7I77_7I74DP_34.vhd` gives it one. When the probe fires, the encoder
module latches the count of every channel armed for it, in hardware, at the
edge. LeafCNC arms channels 00-02, the X, Y and Z scales, for a probing move
(LeafCNC ADR 0052).

## What changed

The file is Mesa's `PIN_7I77_7I74D_34.vhd` with three changes:

- **I/O 16** is the muxed encoder module's probe input,
  `MuxedQCountProbePin`. It was the index line of the 7I77's channels 4 and
  5. A module has one probe input, and all its counters share it.
- **Four muxed counters, not six**: channels 4 and 5 are dropped, and I/O 14
  and 15, their A and B lines, are plain GPIO. With a probe input every
  counter is the larger kind that latches its count on the probe, and six of
  them do not fit the XC6SLX9: ISE 14.7 stopped in placement at 5,466 of
  5,720 LUTs (95 %). Four fit (below). The T20 is larger, and four fill 82 %
  of its logic elements; six have not been tried on it.
- The muxed encoder module reports version **0x84** (`MQCRevP`). The hostmot2
  driver creates `encoder.NN.probe-enable` and `probe-invert` only for that
  version.

**Why I/O 16.** The 7I77 does not wire each encoder to the FPGA on its own
lines. Each A, B and index line carries two channels, switched between them
about four million times a second: channels 0 and 1 on I/O 8-10, 2 and 3 on
I/O 11-13, 4 and 5 on I/O 14-16 (the demultiplexer in Mesa's `hostmot2.vhd`
takes the even channel in one phase and the odd one in the other). Channel 3's
index shares its line with channel 2's, which carries the Z scale's reference
marks, so it cannot be the probe. Channels 4 and 5 are both spare. **The
probe is wired to both their index inputs**, so the line shows it in both
phases, and the FPGA takes the line as the probe input.

What it costs: channels 4 and 5 are gone, index and count both -- they were
spare, and their index line is the probe now. The driver must be asked for
four encoders at most (`num_encoders=4` in the hostmot2 configuration; six is
refused on this firmware), which works on the stock firmware as well. The
7I74 keeps all eight smart-serial channels.

The probe's level is still readable every cycle as `hm2_7i92.0.gpio.016.in`:
hostmot2 gives every pin a GPIO input, whatever module owns it.

`check/` holds a test bench that runs the PIN file's derived constants through
GHDL, the open-source VHDL simulator. Run it from this directory:

```sh
check/check.sh <unpacked hostmot2 source directory>
```

It reports the probe input on I/O 16 and only there, the index lines of
channels 0-1 (I/O 10) and 2-3 (I/O 13), 3 smart-serial channels on port 0 and
8 on port 1, and the muxed encoder's version, 132 (0x84) -- against the 7I92's
sources and against the 7I92T's alike.

## Source

Mesa's `7i92.zip` from mesanet.com (software/parallel/7i92.zip), downloaded
2026-10-08, sha256 `7a603fec07b1f93a466d3050dcd6c1211b4569c5924c665460ecef39fa67b8d3`;
its `configs/hostmot2/source/hostmot2.zip` is dated 2026-09-17. For the
7I92T, Mesa's `7i92t.zip` (software/parallel/7i92t.zip), sha256
`7641bd9db502044259699afedc1ebca24c7d19e38dc1d23afbac01c6239feed9`; its
`configs/hostmot2/source/7i92t-hm2.zip`, the Efinity project with the
sources, is dated 2026-09-17 too. The PIN file keeps Mesa's header: it is
licensed GPL-2.0-or-later or BSD-3-Clause, at your choice.

## Build (Xilinx ISE 14.7 WebPACK, Spartan-6 XC6SLX9-TQ144-2)

1. Unpack `7i92.zip`, then `configs/hostmot2/source/hostmot2.zip`, and open
   `seveni92.xise`.
2. Copy `PIN_7I77_7I74DP_34.vhd` beside the other PIN files and add it to the
   project.
3. Edit `TopEthernet16HostMot2.vhd`:
   - line 89: uncomment `use work.i92_x9card.all;`
   - line 95: comment out `use work.i98_x9card.all;`
   - line 283: replace `use work.PIN_MARSLUKAN_51.all;` with
     `use work.PIN_7I77_7I74DP_34.all;`
4. Use `7i92.ucf` as the constraints file. Generate the programming file
   (`toptethernet16hostmot2.bit`), and rename it `7i92_7i77_7i74DP.bit`.

Built 2026-10-09 with ISE 14.7 WebPACK, headless (`xtclsh`, the project as
above): 5,263 of 5,720 LUTs (92 %), 1,421 of 1,430 slices, 3,970 registers;
every timing constraint met (timing score 0). The bitfile is 341,264 bytes,
sha256 `e06e33ab905ecacc68d1e658ae86c42ed92d367c5a1959dd0a3940e46d53bc50`,
its header naming the part `6slx9tqg144`. The design is full: anything added
to it will not fit.

Mesa (PCW on forum.linuxcnc.org) also builds a bitfile from a PIN file on
request.

## Build (Efinix Efinity, Trion T20F256: the 7I92T and 7I92TH)

`efinity/build-7i92t.sh` does it headless, the way Mesa's project is set up:
it unpacks `7i92t-hm2.zip` from `7i92t.zip` (its sha256 checked), puts
`PIN_7I77_7I74DP_34.vhd` beside the other PIN files and into
`seveni92t.xml`, makes it the one PIN file `TopEthernet16HostMot2_efx.vhd`
uses, sets the place-and-route seed to 2 (Mesa's note for
`PIN_7I77_7I74D_34` on this card) and runs `efx_run.py seveni92t.xml --prj
--flow compile`. Efinity is free but downloaded from Efinix's support
center with an account, so it is not in the container: `efinity/Dockerfile`
is Ubuntu 22.04 with the libraries Efinity loads, and the installation is
mounted (the script's header has the commands).

```sh
MESA_ZIP=/path/to/7i92t.zip EFINITY=/path/to/efinity/2026.1 \
  firmware/efinity/build-7i92t.sh      # or in the container, as its header says
```

Built 2026-10-14 with Efinity 2026.1.132 and its patch 5.14: 16,272 of
19,728 logic elements (82 %), 78 of 204 memory blocks; timing met at the
slow corner (C4, 85 °C), the 100 MHz `procclk` with 0.050 ns of setup and
0.086 ns of hold slack, the design's one clock (`hm2fastclock` is
unconnected in Mesa's top file). `outflow/seveni92t.hex.bin`, renamed
`7i92t_7i77_7i74DP.bin`: 678,650 bytes, the same 256-byte text header and
sync word as Mesa's own `7i92t_7i77_7i74d.bin`. The header names the build's
date and directory, so its sha256 differs from build to build; the 678,394
bytes after it are the bitstream mesaflash writes, and they were the same
in two builds: sha256
`42d84b7f75be0e28c72bb37e1181c61538e0f93f524a9db63bca4b1829fa7fae`
(`tail -c +257 7i92t_7i77_7i74DP.bin | sha256sum`).

## Flash (control stopped)

```sh
D=7i92 F=7i92_7i77_7i74DP.bit           # the 7I92
D=7i92t F=7i92t_7i77_7i74DP.bin         # the 7I92T or 7I92TH
mesaflash --device $D --addr 10.10.10.10 --readhmid       # what runs now
mesaflash --device $D --addr 10.10.10.10 --backup-flash   # keep it
mesaflash --device $D --addr 10.10.10.10 --write $F
mesaflash --device $D --addr 10.10.10.10 --verify $F
mesaflash --device $D --addr 10.10.10.10 --reload
mesaflash --device $D --addr 10.10.10.10 --readhmid       # MuxedQCount 0x84, IO16 probe
```

`--write` writes the user image, at 0x100000 on both cards; the fallback
image at 0 is written only with `--fallback`, never here. The card keeps
that fallback image, so a bad user image is recoverable. On the 7I92T
mesaflash writes the bitstream after 78 bytes of padding and drops the text
header.

Written to the WF41C's 7I92TH on 2026-10-14, its flash backed up first:
`--readhmid` reports four `MuxedQCount` at version 132, `Quad-ProbeM` on
I/O 16 (P2-13), I/O 14 and 15 free, everything else as on the stock
firmware. The high clock reads 175 MHz there, 180 MHz on Mesa's 2022 stock
file; nothing in this layout runs on it.

## Wiring the probe and the tool setter

The probe and the tool setter share this one input, and the control selects
which one feeds it for each probing move. They are never used together, and
a plain OR would not work: a cable-wired probe out of the spindle reads as
triggered.

```
                 +5 V (7I77 TB4 pin 14 or 22)
                  |
Renishaw    --[contact]--+-------- NC o\         relay, coil on a spare output
interface               10k          o-- COM --+--> TB4 pin 15  IDX4
                         |                     +--> TB4 pin 23  IDX5
Setter 5 V out --------------------- NO o     1k
                                                |
                                     GND (TB4 pin 11 or 19)
```

- **Jumpers.** Channels 4 and 5's index inputs single-ended: W11 (IDX4) and
  W3 (IDX5) in the left-hand position. Their A and B jumpers do not matter.
  IDX4- and IDX5- (TB4 pins 16 and 24) stay unconnected.
- **Both inputs, always.** With the probe on only one of them, the line
  would show the probe half the time and an open input the other half.
- **Measure first.** The 7I77's manual does not say whether a single-ended
  input is pulled up when nothing drives it. With the jumpers set and nothing
  connected, measure IDX4+ against ground. Near 0 V: the wiring above, a
  contact switching +5 V with the pull-downs. Near 5 V: it is pulled up; then
  each device pulls the line to ground instead, and the polarity is inverted
  in software (`probe-invert`).
- **Selection.** The relay rests on the spindle probe; a spare output of the
  control energizes it for the setter. The control switches it before a
  probing move and waits for it to settle.
- **Each device's own level**, optionally, to an ordinary input, so the
  control can tell which one fired. Without that both use the line's own
  level, `gpio.016.in`.

## The driver

The hostmot2 driver clears `probe-enable` itself when the probe latches, though
it declares the pin an input. `hm2-host` (driver-hostmot2 v0.6.0 and later)
publishes it both ways and applies it only when it changes, as it does
`index-enable`. Without that it re-arms the latch every cycle and the core
never sees it fire.
