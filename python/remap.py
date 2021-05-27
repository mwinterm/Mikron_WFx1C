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
import hal
import linuxcnc

from interpreter import *
from emccanon import MESSAGE, SET_MOTION_OUTPUT_BIT, CLEAR_MOTION_OUTPUT_BIT,SET_AUX_OUTPUT_BIT,CLEAR_AUX_OUTPUT_BIT

c = linuxcnc.command()

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
        c.error_msg("M910 requires a P value to specify the gearbox block")
    if int(words['p']) not in [1, 2, 3]:
        c.error_msg("M910 error: P value for gearbox block selection has to be 1, 2 or 3")

    if not words.has_key('q'):
        c.error_msg("M910 requires a Q value to specify the gearbox block position")
    if int(words['q']) not in [0, 1, 2]:
        c.error_msg("M910 error: Q value for gearbox block position has to be 0, 1 or 2")

    hal.set_p("gearbox.block_" + str(int(words['p'])) + "_cmd", str(int(words['q'])))



def setspeed(self,**words):
    if self.task==0:
        return INTERP_OK #do nothing in preview or simulation mod

    c = self.blocks[self.remap_level]
    if not c.s_flag:
        self.set_errormsg("S requires a value") 
        return INTERP_ERROR

    speed = int(c.s_number)

    speeds = [0, 40, 50, 63, 80, 100, 125, 160, 200, 250, 315, 400, 500, 630, 800, 1000, 1250, 1600, 2000, 2500, 3150, 4000]
  
    if speed in speeds:
        hal.set_p("geared_spindle.rpms", str(speed))
    else:
        self.set_errormsg("Spindle speed not available")


