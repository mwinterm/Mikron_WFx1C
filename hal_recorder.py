#!/usr/bin/env python
import hal
import time
import csv
from copy import deepcopy

h = hal.component("hal_recorder")
h.newpin("record", hal.HAL_BIT, hal.HAL_IN)
h.newpin("rec-number", hal.HAL_S32, hal.HAL_OUT)

n_inputs = 64  # number of input channels
header = ["Time"]
for i in range(n_inputs):
    h.newpin("in"+str(i), hal.HAL_BIT, hal.HAL_IN)
    header.append("in"+str(i))

h.ready()
h['rec-number'] = 0

try:
    while 1:
        table = []
        row = []
        old_row = []
        start_time = time.time()
        while(h['record']):
            row = [0]
            for i in range(n_inputs):
                row.append(int(h['in'+str(i)]))
            if old_row != row:
                if(len(old_row)):
                    old_row[0] = time.time() - start_time
                    table.append(old_row)
                old_row = deepcopy(row)
                row[0] = time.time() - start_time
                table.append(row)

        if len(table):
            with open('hal_record' + str(h['rec-number']) + '.csv', 'wb') as csvfile:
                my_writer = csv.writer(csvfile, delimiter=',',
                                       quotechar='|', quoting=csv.QUOTE_MINIMAL)

                my_writer.writerow(header)
                for row in table:
                    my_writer.writerow(row)

                h['rec-number'] += 1

except KeyboardInterrupt:
    raise SystemExit
