#!/usr/bin/env python
import hal
import time
from oneshot import Oneshot
from debug import Debug
from linuxcnc_timer import Timer

h = hal.component("drives")

#in-pins
h.newpin("machine_is_on", hal.HAL_BIT, hal.HAL_IN)
h.newpin("tool_change", hal.HAL_BIT, hal.HAL_IN)
h.newpin("toolchange_button", hal.HAL_BIT, hal.HAL_IN)
h.newpin("estop_active", hal.HAL_BIT, hal.HAL_IN)
h.newpin("estop_endswitch_active", hal.HAL_BIT, hal.HAL_IN)
h.newpin("e_stop_contactor", hal.HAL_BIT, hal.HAL_IN)
h.newpin("feed_contactor", hal.HAL_BIT, hal.HAL_IN)
h.newpin("feed_drive_ready", hal.HAL_BIT, hal.HAL_IN)
h.newpin("halui_mode_is_manual", hal.HAL_BIT, hal.HAL_IN)
h.newpin("rpm_surveillance", hal.HAL_BIT, hal.HAL_IN)
h.newpin("vel_xyz", hal.HAL_FLOAT, hal.HAL_IN)

#out-pins
h.newpin("machine_on", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("prepare_toolchange", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("toolchange_button_led", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("axis_1_approve", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("axis_2_approve", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("axis_3_approve", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("feed_driver", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("unclamp_3rd_axis", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("toolchange_button_out", hal.HAL_BIT, hal.HAL_OUT)

h.newparam("tc_button", hal.HAL_BIT, hal.HAL_RW)
h.newparam("drives_active", hal.HAL_BIT, hal.HAL_RW)
h.newparam("debug", hal.HAL_S32, hal.HAL_RW)

h.ready()

tc_button_event = Oneshot(h, "toolchange_button")

h.toolchange_button_led = False
h.toolchange_button_out = False

h.drives_active = False
h.tc_button = False

drives_on_sequence = False
drives_off_sequence = False

d = Debug()

try:
    while True:
        #always clamp 3rd axis when feed-drive not ready (avoid drop of table)
        if not h.feed_drive_ready:
            h.unclamp_3rd_axis = False

        #sequence to switch drives on
        if drives_on_sequence:
            h.feed_driver = True 
            if h.e_stop_contactor and h.feed_contactor:
                h.drives_active = True
                h.axis_1_approve = True
                h.axis_2_approve = True
                h.axis_3_approve = True
                h.unclamp_3rd_axis = True
                h.toolchange_button_led = True
                drives_on_sequence = False
            continue

        #sequence to switch drives off
        if drives_off_sequence:
            h.axis_1_approve = False
            h.axis_2_approve = False
            h.axis_3_approve = False
            h.unclamp_3rd_axis = False
            h.feed_driver = False
            h.prepare_toolchange = True
            h.drives_active = False
            h.toolchange_button_led = False
            drives_off_sequence = False
            continue

        #estop behavior
        if h.estop_active or h.estop_endswitch_active:
                h.debug = 1
                drives_off_sequence = True
        else:
            # create the toolchange command
            if tc_button_event.up():
                h.tc_button = True

            # if no tool-change is requested and you are not in manual mode
            if not h.tool_change and h.drives_active and not h.halui_mode_is_manual:
                h.debug = 4
                h.toolchange_button_out = False
                h.prepare_toolchange = False

            #switch machine on if not yet on
            if not h.machine_is_on and h.tc_button:
                h.debug = 5
                h.machine_on = True
                h.tc_button = False
                continue
            
            #Switch drives on in manual mode
            if h.halui_mode_is_manual and h.machine_is_on and not h.drives_active and h.tc_button:
                h.debug = 6
                drives_on_sequence = True
                h.tc_button = False

            #Switch off drives in manual mode
            if h.halui_mode_is_manual and h.drives_active and h.tc_button and not h.rpm_surveillance and not h.vel_xyz:
                h.debug = 7
                drives_off_sequence = True
                h.tc_button = False

            #Switch drives off for toolchange in automatic operation
            if h.tool_change and not h.prepare_toolchange and not h.rpm_surveillance and not h.vel_xyz:
                h.debug = 9
                drives_off_sequence = True

            #Switch drives on in automatic operation
            if h.prepare_toolchange and h.tc_button:
                h.debug = 10
                drives_on_sequence = True
                h.tc_button = False

except KeyboardInterrupt:
    raise SystemExit
