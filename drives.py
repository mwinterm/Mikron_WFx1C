#!/usr/bin/env python
import hal
import time

h = hal.component("drives")

#in-pins
h.newpin("machine_is_on", hal.HAL_BIT, hal.HAL_IN)
h.newpin("tool_change", hal.HAL_BIT, hal.HAL_IN)
h.newpin("toolchange_button", hal.HAL_BIT, hal.HAL_IN)
h.newpin("e_stop_contactor", hal.HAL_BIT, hal.HAL_IN)
h.newpin("feed_contactor", hal.HAL_BIT, hal.HAL_IN)
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
h.newparam("tc_button_old", hal.HAL_BIT, hal.HAL_RW)
h.newparam("drives_active", hal.HAL_BIT, hal.HAL_RW)

h.ready()

h.toolchange_button_led = False
h.toolchange_button_out = False

start_seq_comp = False
h.drives_active = False
h.tc_button = False
h.tc_button_old = False

try:
    while True:

        if h.toolchange_button and not h.tc_button_old:
            h.tc_button = True
            h.tc_button_old = True
        elif not h.toolchange_button:
            h.tc_button_old = False

        if not h.tool_change and h.drives_active and not h.halui_mode_is_manual:
            h.toolchange_button_out = False
            h.prepare_toolchange = False

        #switch machine on if not yet on
        if not h.machine_is_on:
            start_seq_comp = False
            if h.toolchange_button:
                h.machine_on = True
            
        if h.machine_is_on and not start_seq_comp:
            h.feed_driver = True
            if not h.e_stop_contactor and h.feed_contactor:
                h.axis_1_approve = True
                h.axis_2_approve = True
                h.axis_3_approve = True
                h.unclamp_3rd_axis = True
                h.drives_active = True
                h.toolchange_button_led = True
                start_seq_comp = True

        
        if start_seq_comp:
            if h.halui_mode_is_manual and h.drives_active and h.tc_button and not h.rpm_surveillance and not h.vel_xyz:
                h.unclamp_3rd_axis = False
                h.axis_1_approve = False
                h.axis_2_approve = False
                h.axis_3_approve = False
                h.feed_driver = False
                h.prepare_toolchange = True
                h.drives_active = False
                h.toolchange_button_led = False
                h.tc_button = False
            elif h.halui_mode_is_manual and not h.drives_active and h.tc_button:
                h.prepare_toolchange = False
                h.feed_driver = True
                h.axis_1_approve = True
                h.axis_2_approve = True
                h.axis_3_approve = True
                h.unclamp_3rd_axis = True
                h.toolchange_button_led = True
                h.drives_active = True
                h.tc_button = False
            elif h.tool_change and not h.prepare_toolchange:
                h.unclamp_3rd_axis = False
                h.axis_1_approve = False
                h.axis_2_approve = False
                h.axis_3_approve = False
                h.feed_driver = False
                h.prepare_toolchange = True
                h.toolchange_button_led = False
                h.drives_active = False
            elif h.prepare_toolchange and h.tc_button:
                # h.prepare_toolchange = False
                h.feed_driver = True
                h.axis_1_approve = True
                h.axis_2_approve = True
                h.axis_3_approve = True
                h.unclamp_3rd_axis = True
                h.drives_active = True
                h.toolchange_button_led = True
                h.toolchange_button_out = True
                h.tc_button = False

except KeyboardInterrupt:
    raise SystemExit
