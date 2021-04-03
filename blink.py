#!/usr/bin/env python
import hal
import time
h = hal.component("blink")
h.newpin("auto", hal.HAL_BIT, hal.HAL_IN)
h.newpin("single", hal.HAL_BIT, hal.HAL_IN)
h.newpin("jog", hal.HAL_BIT, hal.HAL_IN)
h.newpin("is_running", hal.HAL_BIT, hal.HAL_IN)
h.newpin("is_paused", hal.HAL_BIT, hal.HAL_IN)
h.newpin("red", hal.HAL_BIT, hal.HAL_OUT)
h.newpin("green", hal.HAL_BIT, hal.HAL_OUT)
h.ready()

ms_count = 0

try:
    while 1:
        ms_count = int(time.clock()*1000) % 1000

        if (h['auto'] and h['is_running']):
            h['green'] = True
            h['red'] = False
        elif (h['auto'] and h['is_paused']):
            h['green'] = False
            h['red'] = True
        elif (h['single'] and ms_count < 500):
            h['green'] = False
            h['red'] = True
        elif (h['single'] and ms_count > 500):
            h['green'] = True
            h['red'] = False
        elif (h['jog'] and h['is_running'] and (ms_count % 500 < 250)):
            h['green'] = True
            h['red'] = False
        elif (h['jog'] and h['is_running'] and (ms_count % 500 > 250)):
            h['green'] = False
            h['red'] = False
        elif (h['jog'] and h['is_paused']):
            h['green'] = False
            h['red'] = True
        else:
            h['green'] = False
            h['red'] = False
except KeyboardInterrupt:
    raise SystemExit
