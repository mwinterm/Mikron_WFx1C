#!/usr/bin/env python
import hal
import time
import linuxcnc
from linuxcnc_timer import Timer


c = linuxcnc.command()


h = hal.component("gearbox")
h.newpin("spindle_on", hal.HAL_BIT, hal.HAL_IN)
h.newpin("forward", hal.HAL_BIT, hal.HAL_IN)
h.newpin("reverse", hal.HAL_BIT, hal.HAL_IN)
h.newpin("rpm_surveillance", hal.HAL_BIT, hal.HAL_IN)
h.newpin("spindle_contactor", hal.HAL_BIT, hal.HAL_IN)

h.newpin("spindle_motor", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("soft_start", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("cw", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("ccw", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("stage_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("stage_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("spindle_break", hal.HAL_BIT, hal.HAL_OUT)
h.ready()


soft_start_timer = Timer(3.0)
start_check_timer = Timer(0.5)

h.stage_1 = True

try:
    while True:
        
        if h.spindle_on:
            if h.forward:
                h.cw = True
                h.ccw = False
            elif h.reverse:
                h.cw = False
                h.ccw = True
            else:
                c.error_msg("No spindle direction set.") 

            h.spindle_break = False
            h.spindle_motor = True
            start_check_timer.start()
            if not start_check_timer():
                if not h.rpm_surveillance:
                    c.error_msg("Spindle start: Spindle not turning.")
                if not h.spindle_contactor: 
                    c.error_msg("Spindle start: Spindle contactor problem.")

            soft_start_timer.start()
            if soft_start_timer():
                h.soft_start = True

        else:
            h.spindle_motor = False
            h.soft_start = False
            h.cw = False
            h.ccw = False

            if h.rpm_surveillance:
                h.spindle_break = True
            else:
                h.spindle_break = False
            





except KeyboardInterrupt:
    raise SystemExit
