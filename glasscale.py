#!/usr/bin/env python
import hal
import time
h = hal.component("glasscale")
h.newpin("count_in", hal.HAL_S32, hal.HAL_IN)
h.newpin("raw_count_in", hal.HAL_S32, hal.HAL_IN)
h.newpin("count_out", hal.HAL_S32, hal.HAL_OUT)
h.newpin("index_enable", hal.HAL_BIT, hal.HAL_IO)
h.ready()

my_count = 0
h['count_out'] = 0
h['index_enable'] = True


try:
    # main while-loop
    while 1:
        my_count = h['raw_count_in'] - h['count_in']

        if not h['index_enable']:
            my_count = h['raw_count_in'] - h['count_in']
            h['count_out'] = my_count
            print(my_count)
            h['index_enable'] = True
            time.sleep(0.1)
            # h['index_enable'] = False





except KeyboardInterrupt:
    raise SystemExit
