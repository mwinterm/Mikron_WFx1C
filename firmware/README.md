# 7i92_7i77_7i74DP: the 7I92's firmware with a probe input

The WF41C's 7I92 runs Mesa's stock `7i92_7i77_7i74D` layout: a 7I77 on one
connector (six muxed encoders, the analog outputs, field I/O) and a 7I74 on
the other (eight smart-serial channels). That firmware has no probe input,
so a touch probe can only be read once per servo cycle.

`PIN_7I77_7I74DP_34.vhd` gives it one. When the probe fires, the encoder
module latches the count of every channel armed for it, in hardware, at the
edge. LeafCNC arms channels 00-02, the X, Y and Z scales, for a probing move
(LeafCNC ADR 0052).

## What changed

The file is Mesa's `PIN_7I77_7I74D_6SS_34.vhd` (the same layout with port 1
cut to six smart-serial channels) with two changes:

- **I/O 27**, the 7I74's channel 6 receive pair, is the muxed encoder
  module's probe input, `MuxedQCountProbePin`. A module has one probe input,
  and all six counters share it.
- The muxed encoder module reports version **0x84** (`MQCRevP`). The hostmot2
  driver creates `encoder.NN.probe-enable` and `probe-invert` only for that
  version.

What it costs: port 1's channels 6 and 7 are gone, and I/O 28 and 31-33 are
plain GPIO. The WF41C uses channels 0 (7I73), 2 (7I70) and 4 (7I84) there, and
`sserial_port_1=10000000` reads the same.

The probe's level is still readable every cycle as `hm2_7i92.0.gpio.027.in`:
hostmot2 gives every pin a GPIO input, whatever module owns it.

`check/` holds a test bench that runs the PIN file's derived constants through
GHDL, the open-source VHDL simulator. Run it from this directory:

```sh
check/check.sh <unpacked hostmot2 source directory>
```

It reports that the probe pin exists, that port 0 has 3 channels and port 1
has 6, and that the muxed encoder's version is 132 (0x84).

## Source

Mesa's `7i92.zip` from mesanet.com (software/parallel/7i92.zip), downloaded
2026-10-08, sha256 `7a603fec07b1f93a466d3050dcd6c1211b4569c5924c665460ecef39fa67b8d3`;
its `configs/hostmot2/source/hostmot2.zip` is dated 2026-09-17. The PIN file
keeps Mesa's header: it is licensed GPL-2.0-or-later or BSD-3-Clause, at your
choice.

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

Mesa (PCW on forum.linuxcnc.org) also builds a bitfile from a PIN file on
request.

## Flash (control stopped)

```sh
mesaflash --device 7i92 --addr 10.10.10.10 --readhmid       # what runs now
mesaflash --device 7i92 --addr 10.10.10.10 --backup-flash   # keep it
mesaflash --device 7i92 --addr 10.10.10.10 --write 7i92_7i77_7i74DP.bit
mesaflash --device 7i92 --addr 10.10.10.10 --verify 7i92_7i77_7i74DP.bit
mesaflash --device 7i92 --addr 10.10.10.10 --reload
mesaflash --device 7i92 --addr 10.10.10.10 --readhmid       # MuxedQCount 0x84, IO27 probe
```

The card keeps a fallback image, so a bad user image is recoverable.

## Wiring the probe and the tool setter

The probe and the tool setter share this one input, and the control selects
which one feeds it for each probing move. They are never used together, and
a plain OR would not work: a cable-wired probe out of the spindle reads as
triggered.

- **Selection.** A relay driven by one of the control's outputs (a 7I84 or
  7I77 field output) connects either the probe interface's contact or the
  setter's 5 V output to the adapter below. The relay's rest position is the
  probe.
- **Each device's own level** also goes to an ordinary input (the 7I70 had
  free inputs in this configuration). The control can then check that the
  selected one is the one that fired.
- **Adapter to RS-422.** Jack 6 is an RS-422 receiver with 120 ohm
  termination, so the signal goes in through one line driver, for example an
  AM26C31 powered from the jack:

  | Jack 6 (RJ45) | Use |
  |---|---|
  | 7, 8 (+5 V) | driver's VCC, and the contact's supply |
  | 4, 5 (GND) | driver's GND |
  | 6 (RX+) | driver output Y |
  | 3 (RX-) | driver output Z |

  The driver's input has a 10 k pull-down. The probe interface's contact
  switches it to +5 V, or the setter's 5 V output drives it. Tie enable G to
  +5 V and /G to GND. Which level means "triggered" is set in software
  (`probe-invert`).

## The driver

The hostmot2 driver clears `probe-enable` itself when the probe fires.
`hm2-host` (driver-hostmot2) must publish that pin both ways and apply it only
when it changes, as it already does for `index-enable`. Otherwise it re-arms
the latch every cycle and the core never sees it fire.
