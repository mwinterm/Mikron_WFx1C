-- What the PIN file makes of the card, without ISE: which I/O is the muxed
-- encoder module's probe input, which channel pairs keep their index, how
-- many smart-serial channels each port has, and the version the module
-- reports. Run by check.sh under GHDL.
library ieee; use ieee.std_logic_1164.all; use ieee.std_logic_arith.all; use ieee.std_logic_unsigned.all;
use work.IDROMConst.all;
use work.PIN_7I77_7I74DP_34.all;
use work.InputPinsPerModule.all;
entity pin_check is end;
architecture a of pin_check is begin
  process
    variable probes : integer := 0;
  begin
    for i in PinDesc'range loop
      if PinDesc(i)(15 downto 8) = MuxedQCountTag then
        if PinDesc(i)(7 downto 0) = MuxedQCountProbePin then
          report "probe input: I/O " & integer'image(i);
          probes := probes + 1;
        elsif PinDesc(i)(7 downto 0) = MuxedQCountIDXPin then
          report "index of channels " & integer'image(2 * conv_integer(PinDesc(i)(23 downto 16)))
            & " and " & integer'image(2 * conv_integer(PinDesc(i)(23 downto 16)) + 1)
            & ": I/O " & integer'image(i);
        end if;
      end if;
    end loop;
    report "probe inputs: " & integer'image(probes);
    report "sserial 0 channels: " & integer'image(InputPinsPerModule(PinDesc, SSerialTag, 0));
    report "sserial 1 channels: " & integer'image(InputPinsPerModule(PinDesc, SSerialTag, 1));
    report "muxed encoder version: " & integer'image(conv_integer(ModuleID(3).Version));
    wait;
  end process;
end;
