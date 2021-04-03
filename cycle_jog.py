#!/usr/bin/env python
import hal
import time
h = hal.component("cycle_jog")
h.newpin("active", hal.HAL_BIT, hal.HAL_IN)
h.newpin("count_in", hal.HAL_S32, hal.HAL_IN)
h.newpin("delta_t", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("speed_scale", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("speed", hal.HAL_FLOAT, hal.HAL_OUT)
h.ready()

speed = 0.0
old_count = h['count_in']
new_count = old_count
old_time = time.time()
new_time = old_time
count_out = old_count

try:
    # wait delta_t is set to avoid division by 0
    while h['delta_t'] == 0.0:
        time.sleep(0.1)

    # main while-loop
    while 1:
        new_time = time.time()
        new_count = h['count_in']
        while (new_time - old_time) < h['delta_t']:
            time.sleep(0.05)
            new_time = time.time()
            new_count = h['count_in']

        speed = (new_count-old_count)/(new_time-old_time) * h['speed_scale']

        if speed > 0.0:
            speed = min(speed, 1.0)
        else:
            speed = max(speed, -1.0)

        if h['active']:
            h['speed'] = speed
        else:
            h['speed'] = 1.0

        old_time = new_time
        old_count = new_count


except KeyboardInterrupt:
    raise SystemExit
