#!/usr/bin/env python
import hal
import time
import linuxcnc
from linuxcnc_timer import Timer
#from debug import Debug

c = linuxcnc.command()

# c.error_msg('Error')
# c.text_msg('Text')
# c.display_msg('Display')

h = hal.component("lubrication")

h.newparam("lub_cycle_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("lub_interval_time", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("num_cycles", hal.HAL_S32, hal.HAL_RW)
h.newparam("start_cycles_pause", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("lub_warning_interval", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("max_lub_pressure_delay", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint0_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_dist", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint0_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint1_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)
h.newparam("joint2_lub_hubs", hal.HAL_FLOAT, hal.HAL_RW)

h.newparam("lub_command", hal.HAL_BIT, hal.HAL_RW)
h.newparam("paused", hal.HAL_BIT, hal.HAL_RW)
h.newparam("lub_interval_timer", hal.HAL_FLOAT, hal.HAL_RO)


h.newpin("machine_is_on", hal.HAL_BIT, hal.HAL_IN)
h.newpin("lub_pressure", hal.HAL_BIT, hal.HAL_IN)
h.newpin("joint0_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint1_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint2_integ", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint0_vel", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint1_vel", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("joint2_vel", hal.HAL_FLOAT, hal.HAL_IN)

h.newpin("lub_pump", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("integ_reset", hal.HAL_BIT, hal.HAL_OUT)


h.ready()

#wait until machine is ready
while not h.machine_is_on:
    time.sleep(0.1)

#initialize 
joint0_vel_old = 1.0
joint1_vel_old = 1.0
joint2_vel_old = 1.0
joint0_hubs = 0
joint1_hubs = 0
joint2_hubs = 0

#initialize timers
lub_interval_timer = Timer(h.lub_interval_time)
lub_cycle_timer = Timer(h.lub_cycle_time)
pressure_delay_timer = Timer(h.max_lub_pressure_delay)
pause_warning_timer = Timer(h.lub_warning_interval)
start_cycles_pause_timer = Timer(h.start_cycles_pause)

#lub_debug = Debug("lubrication debug")

try:
    while 1:
        if h.machine_is_on:

            #do initial lubrications at startup or after estop
            if h.num_cycles < 0 and not start_cycles_pause_timer():
                h.lub_command = True

            #do distance traveled based lubrication
            if h.joint0_integ > h.joint0_lub_dist or h.joint1_integ > h.joint1_lub_dist or h.joint2_integ > h.joint2_lub_dist:
                h.lub_command = True

            #count direction changes per axis
            if h.joint0_vel*joint0_vel_old < 0:
                joint0_vel_old = h.joint0_vel
                joint0_hubs += 1

            if h.joint1_vel*joint1_vel_old < 0:
                joint1_vel_old = h.joint1_vel
                joint1_hubs += 1

            if h.joint2_vel*joint2_vel_old < 0:
                joint2_vel_old = h.joint2_vel
                joint2_hubs += 1

            #do hubs based lubrication
            if joint0_hubs > h.joint0_lub_hubs or joint1_hubs > h.joint1_lub_hubs or joint2_hubs > h.joint2_lub_hubs:
                h.lub_command = True

            #do time based lubrication
            h.lub_interval_timer = lub_interval_timer.time()
            if lub_interval_timer.alarm():
                h.lub_command = True

            #execute lubrication
            if h.lub_command & h.paused:
                pause_warning_timer.start()
                h.lub_pump = False
                if pause_warning_timer.alarm():
                    c.text_msg("Warning: Lubrication is paused")
                    pause_warning_timer.start()
            
            elif h.lub_command and not h.paused: 
                h.lub_pump = True
                pressure_delay_timer.start()
                pause_warning_timer.stop()

            #start the timer for lubrication based on pressure
            if h.lub_command and h.lub_pressure:
                pressure_delay_timer.stop()
                lub_cycle_timer.start()
                
            #check if it takes too long to build pressure 
            if pressure_delay_timer.alarm():
                c.error_msg("Lubrication not working, no pressure building up.")
                pressure_delay_timer.start()

            #end the lub cycle
            if h.lub_pressure and h.lub_command and not lub_cycle_timer():
                h.lub_command = False
                h.lub_pump = False
                h.integ_reset = True
                h.num_cycles +=1
                joint0_hubs = 0
                joint1_hubs = 0
                joint2_hubs = 0
                lub_interval_timer.restart()
                start_cycles_pause_timer.stop()
                lub_cycle_timer.stop()
                if(h.num_cycles < 0):
                    start_cycles_pause_timer.start()

except KeyboardInterrupt:
    raise SystemExit
