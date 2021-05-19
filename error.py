#!/usr/bin/env python
import hal
import time
import linuxcnc


c = linuxcnc.command()

# c.error_msg('Error')
# c.text_msg('Text')
# c.display_msg('Display')


h = hal.component("error")
h.newpin("estop_endswitch", hal.HAL_BIT, hal.HAL_IN)
h.newpin("drive_surveillance", hal.HAL_BIT, hal.HAL_IN)
h.ready()

hal.connect("estop_endswitch", "_E1_emergency_stop_end_switch")
estop_endswitch_state = False
hal.connect("drive_surveillance", "_E24_surveillance_feed_drive")
surveillance_feed_drive_state = False

try:
    while True:
        if h.estop_endswitch and not estop_endswitch_state:
            c.error_msg("E-stop emergency switch triggered.")
            estop_endswitch_state = True
        elif not h.estop_endswitch and estop_endswitch_state:
            estop_endswitch_state = False

        if h.drive_surveillance and not surveillance_feed_drive_state:
            c.error_msg("Feed drives not ready. Restart Machine.")
            surveillance_feed_drive_state= True
        elif not h.drive_surveillance and surveillance_feed_drive_state:
             surveillance_feed_drive_state = False


except KeyboardInterrupt:
    raise SystemExit
