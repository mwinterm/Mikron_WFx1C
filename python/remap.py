#   This is a component of LinuxCNC
#   Copyright 2011, 2013, 2014 Dewey Garrett <dgarrett@panix.com>,
#   Michael Haberler <git@mah.priv.at>
#
#   This program is free software; you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation; either version 2 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program; if not, write to the Free Software
#   Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#
from stdglue import *

import hal
import linuxcnc
import emccanon

from interpreter import *

cmd = linuxcnc.command()

# Lubrication cycle
def m901(self, **words):
    if words.has_key('p'):
        if words['p'] == 0:
            hal.set_p("lubrication.paused","False")
        elif words['p'] == 1:
            hal.set_p("lubrication.paused","True")
    else: 
        hal.set_p("lubrication.lub_command","True")
    return INTERP_OK


def m910(self, **words):
    if not words.has_key('p'):
        cmd.error_msg("M910 requires a P value to specify the gearbox block")
    if int(words['p']) not in [1, 2, 3]:
        cmd.error_msg("M910 error: P value for gearbox block selection has to be 1, 2 or 3")

    if not words.has_key('q'):
        cmd.error_msg("M910 requires a Q value to specify the gearbox block position")
    if int(words['q']) not in [1, 2, 3]:
        cmd.error_msg("M910 error: Q value for gearbox block position has to be 1, 2 or 3")

    hal.set_p("gearbox.block_" + str(int(words['p'])) + "_cmd", str(int(words['q'])))

def setspeed(self, **words):
    try:
        c = self.blocks[self.remap_level]
        if not c.s_flag:
            self.set_errormsg("S requires a value") 
            return INTERP_ERROR
        self.params["speed"] = c.s_number

        speeds = {
            0: [2, 3, 2, 1],
            40: [2, 3, 3, 1],
            50: [3, 3, 3, 1],
            63: [1, 3, 3, 1],
            80: [2, 1, 3, 1],
            100: [3, 1, 3, 1],
            125: [1, 1, 3, 1],
            160: [2, 2, 3, 1],
            200: [3, 2, 3, 1],
            250: [1, 2, 3, 1],
            315: [2, 3, 1, 1],
            400: [3, 3, 1, 1],
            500: [1, 3, 1, 1],
            630: [2, 1, 1, 1],
            800: [3, 1, 1, 1],
            1000: [1, 1, 1, 1],
            1250: [2, 2, 1, 1],
            1600: [3, 2, 1, 1],
            2000: [1, 2, 1, 1],
            2500: [2, 2, 1, 2],
            3150: [3, 2, 1, 2],
            4000: [1, 2, 1, 2]
            }

        if c.s_number in speeds:
            gear = speeds[c.s_number]
            hal.set_p("gearbox.block_1_cmd", str(gear[0]))
            hal.set_p("gearbox.block_2_cmd", str(gear[1]))
            hal.set_p("gearbox.block_3_cmd", str(gear[2]))
            if gear[3] == 1:
                hal.set_p("gearbox.stage_1", '1')
                hal.set_p("gearbox.stage_2", '0')
            else:
                hal.set_p("gearbox.stage_1", '0')
                hal.set_p("gearbox.stage_2", '1')

        emccanon.enqueue_SET_SPINDLE_SPEED(0, c.s_number)
        print("SETSPEED: Here I am")
        return INTERP_OK

    except Exception, e:
        self.set_errormsg("Setspeed: %s" % (e))
        return INTERP_ERROR


def setspeed_new(self,**words):    
    speed = 0
    c = self.blocks[self.remap_level]
    if c.s_flag:
        speed = int(c.s_number)
    else: 
        cmd.error_msg("S command without speed value was provided")
        
    speeds = {
        0: [2, 3, 2, 1],
        40: [2, 3, 3, 1],
        50: [3, 3, 3, 1],
        63: [1, 3, 3, 1],
        80: [2, 1, 3, 1],
        100: [3, 1, 3, 1],
        125: [1, 1, 3, 1],
        160: [2, 2, 3, 1],
        200: [3, 2, 3, 1],
        250: [1, 2, 3, 1],
        315: [2, 3, 1, 1],
        400: [3, 3, 1, 1],
        500: [1, 3, 1, 1],
        630: [2, 1, 1, 1],
        800: [3, 1, 1, 1],
        1000: [1, 1, 1, 1],
        1250: [2, 2, 1, 1],
        1600: [3, 2, 1, 1],
        2000: [1, 2, 1, 1],
        2500: [2, 2, 1, 2],
        3150: [3, 2, 1, 2],
        4000: [1, 2, 1, 2]
        }


    if speed in speeds:
        gear = speeds[speed]
        hal.set_p("gearbox.block_1_cmd", str(gear[0]))
        hal.set_p("gearbox.block_2_cmd", str(gear[1]))
        hal.set_p("gearbox.block_3_cmd", str(gear[2]))
        if gear[3] == 1:
            hal.set_p("gearbox.stage_1", '1')
            hal.set_p("gearbox.stage_2", '0')
        else:
            hal.set_p("gearbox.stage_1", '0')
            hal.set_p("gearbox.stage_2", '1')

        emccanon.enqueue_SET_SPINDLE_SPEED(0, float(speed))

        print("gearbox set")
    else:
        cmd.error_msg("Spindle speed not available")


