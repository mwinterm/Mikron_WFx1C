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

h.newpin("block_1_cmd", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_cmd", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_cmd", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_1_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_1_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_2_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_1", hal.HAL_BIT, hal.HAL_IN)
h.newpin("block_3_2", hal.HAL_BIT, hal.HAL_IN)
h.newpin("current_measurement", hal.HAL_BIT, hal.HAL_IN)

h.newpin("block_1_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_1_backward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_2_backward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_forward", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("block_3_backward", hal.HAL_BIT, hal.HAL_OUT)

h.ready()


soft_start_timer = Timer(3.0)
start_check_timer = Timer(0.5)
current_timer = Timer(1.0)
block_reset_timer = Timer(0.15)
block_spindle_timer = Timer(0.2)

current_alarm_type = ""
spindle_on = False

block_1_pos = 0
block_2_pos = 0
block_3_pos = 0
block_pos = 0
block_cmd = 0

#just for initialization
block_forward = h.block_1_forward 
block_backward = h.block_1_backward

h.stage_1 = True

try:
    while True:

        #getting gearbox positions
        for block in ['block_1_', 'block_2_', 'block_3_']:
            b_1 = block + '1'
            b_2 = block + '2'
            if getattr(h, b_1) and getattr(h, b_2):
                locals()[block + 'pos'] = 0 
            if not getattr(h, b_1) and getattr(h, b_2):
                locals()[block + 'pos'] = 1 
            if getattr(h, b_1) and not getattr(h, b_2):
                locals()[block + 'pos'] = 2 

        #starting / stopping spindle        
        if h.spindle_on or spindle_on:
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

        #setting gearbox
        if not h.spindle_on:
            
            for block in ['block_1_', 'block_2_', 'block_3_']:
                b_1 = block + '1'
                b_2 = block + '2'
                block_forward = getattr(h, block + 'forward')
                block_backward = getattr(h, block + 'backward')
                block_cmd = getattr(h, block + 'cmd')
                block_pos = locals()[block + 'pos']
                if block_pos != block_cmd:
                    break

            #release any blockage
            if current_timer.alarm():
                if current_alarm_type == "":
                    if block_forward:
                        current_alarm_type = "block_forward"
                    elif block_backward:
                        current_alarm_type = "block_backward"

                if current_alarm_type == "block_forward":
                    block_forward = False
                    block_reset_timer.start()
                    if block_reset_timer():
                        block_backward = True
                        continue
                    else:
                        block_backward = False
                        block_spindle_timer.start()
                        continue

                elif current_alarm_type == "block_1_backward":
                    block_backward = False
                    block_reset_timer.start()
                    if block_reset_timer():
                        block_forward = True
                        continue
                    else:
                        block_forward = False
                        block_spindle_timer.start()
                        continue

                if block_spindle_timer():
                    spindle_on = True
                    continue
                else:
                    spindle_on = False

                current_timer.stop()
                current_alarm_type = ""

            #Set the gearbox
            if block_cmd > block_pos:
                block_forward = True
                block_backward = False
                if h.current_measurement:
                    current_timer.start()
                else:
                    current_timer.stop()
            elif block_cmd < block_pos:
                block_forward = False
                block_backward = True
                if h.current_measurement:
                    current_timer.start()
                else:
                    current_timer.stop()
            elif block_cmd == block_pos:
                block_forward = False
                block_backward = False


except KeyboardInterrupt:
    raise SystemExit
