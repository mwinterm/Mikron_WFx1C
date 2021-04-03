#!/usr/bin/env python
import hal
import time
h = hal.component("progressive_jog")
h.newpin("count_in", hal.HAL_S32, hal.HAL_IN)
h.newpin("delta_t", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("speed_scale", hal.HAL_FLOAT, hal.HAL_IN)
h.newpin("count_out", hal.HAL_S32, hal.HAL_OUT)
h.newpin("speed", hal.HAL_FLOAT, hal.HAL_OUT)
h.ready()

speed = 0.0
old_count = h['count_in']
new_count = old_count
old_time = time.time()
new_time = old_time
count_out = old_count

try:
    while 1:
        new_time = time.time()
        new_count = h['count_in']
        while (new_count == old_count) or ((new_time - old_time) < h['delta_t']):
            time.sleep(0.05)
            new_time = time.time()
            new_count = h['count_in']

        speed = abs((new_count-old_count) /
                    (new_time-old_time) * h['speed_scale'])
        h['speed'] = speed

        count_out += int((1.0 + speed)*(new_count - old_count))

        h['count_out'] = count_out
        old_time = new_time
        old_count = new_count


except KeyboardInterrupt:
    raise SystemExit
