library ieee; use ieee.std_logic_1164.all; use ieee.std_logic_arith.all; use ieee.std_logic_unsigned.all;
use work.IDROMConst.all;
use work.PIN_7I77_7I74DP_34.all;
use work.PinExists.all;
use work.InputPinsPerModule.all;
entity pin_check is end;
architecture a of pin_check is begin
  process begin
    report "probe pin exists: " & boolean'image(PinExists(PinDesc, MuxedQCountTag, MuxedQCountProbePin));
    report "sserial 0 channels: " & integer'image(InputPinsPerModule(PinDesc, SSerialTag, 0));
    report "sserial 1 channels: " & integer'image(InputPinsPerModule(PinDesc, SSerialTag, 1));
    report "muxed encoder version: " & integer'image(conv_integer(ModuleID(3).Version));
    wait;
  end process;
end;
