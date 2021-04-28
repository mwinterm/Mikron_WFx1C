# script to plot hal-records
import sys
import getopt
import pandas as pd
import matplotlib.pyplot as plt
import os


try:
    opts, args = getopt.getopt(sys.argv[1:], "hi:f:t:s", [
                               "input=", "filter=", "save=", "time="])
except getopt.GetoptError:
    print 'hal_plot.py -i <inputfile> -f <filter: zero | constant> -s <file_format> -t <interval>'
    sys.exit(2)


filearg = ''
filter = ''
save = ''
timearg = ''

for opt, arg in opts:
    if opt == '-h':
        print 'hal_plot.py -i <inputfile> -f <filter: zero | constant | gearbox> -s <file_format>'
        sys.exit()
    elif opt in ("-i", "--input"):
        filearg = arg
    elif opt in ("-f", "--filter"):
        filter = arg
    elif opt in ("-s", "--save"):
        save = arg
    elif opt in ("-t", "--time"):
        timearg = arg

print('Input file argument is: ', filearg)
print('Filter is: ', filter)
print('Save Format is: ', save)
print('Time interval is: ', timearg)

column_list = []
time_interval = []
if filter.startswith("[") and filter.endswith("]"):
    filter = filter.replace('[', '')
    filter = filter.replace(']', '')
    filter = filter.replace(' ', '')
    column_list = list(filter.split(','))

if timearg.startswith("[") and timearg.endswith("]"):
    timearg = timearg.replace('[', '')
    timearg = timearg.replace(']', '')
    timearg = timearg.replace(' ', '')
    time_interval = list(timearg.split(','))
    for i in range(len(time_interval)):
        time_interval[i] = float(time_interval[i])

if(filter == 'gearbox'):
    column_list = [
        'in17_E17_gear_set_block1_1',
        'in18_E18_gear_set_block1_2',
        'in19_E19_gear_set_block2_1',
        'in20_E20_gear_set_block2_2',
        'in21_E21_gear_set_block3_1',
        'in22_E22_gear_set_block3_2',
        'in23_E23_current_measurement',
        'in48_A16_block_1_forward',
        'in49_A17_block_1_backward',
        'in50_A18_block_2_forward',
        'in51_A19_block_2_backward',
        'in52_A20_block_3_forward',
        'in53_A21_block_3_backward'
    ]

filename = ''
record = pd.DataFrame()

for filename in os.listdir(os.getcwd()):
    if filename.startswith(filearg) and filename.endswith(".csv"):

        record = pd.read_csv(filename)
        record.rename(columns={
            'in0': 'in0_E0_emergency_stop_button',
            'in1': 'in1_E1_emergency_stop_end_switch',
            'in2': 'in2_E2_ZENTR_MIKROSK?',
            'in3': 'in3_E3_emergency_stop_feedback',
            'in4': 'in4_E4_central_lubrication',
            'in5': 'in5_E5_surveillance_coolant',
            'in6': 'in6_E6_door_lock',
            'in7': 'in7_E7_door_surveillance',
            'in8': 'in8_E8_prepare',
            'in9': 'in9_E9_feed_contactor',
            'in10': 'in10_E10_emergency_stop_contactor',
            'in11': 'in11_E11_spindle_contactor',
            'in12': 'in12_E12_free',
            'in13': 'in13_E13_free',
            'in14': 'in14_E14_free',
            'in15': 'in15_E15_temp_surveillance',
            'in16': 'in16_E16_rpm_surveillance',
            'in17': 'in17_E17_gear_set_block1_1',
            'in18': 'in18_E18_gear_set_block1_2',
            'in19': 'in19_E19_gear_set_block2_1',
            'in20': 'in20_E20_gear_set_block2_2',
            'in21': 'in21_E21_gear_set_block3_1',
            'in22': 'in22_E22_gear_set_block3_2',
            'in23': 'in23_E23_current_measurement',
            'in24': 'in24_E24_surveillance_feed_drive',
            'in25': 'in25_E25_feed_drive_ready',
            'in26': 'in26_E26_free',
            'in27': 'in27_E27_refpoint_axis_1',
            'in28': 'in28_E28_refpoint_axis_2',
            'in29': 'in29_E29_refpoint_axis_3',
            'in30': 'in30_E30_refpoint_axis_4',
            'in31': 'in31_E31_door_surveillance',
            'in32': 'in32_A0_coolant_pump',
            'in33': 'in33_A1_central_lubrication',
            'in34': 'in34_A2_soft_spindle_start',
            'in35': 'in35_A3_spindle_motor',
            'in36': 'in36_A4_M211_stage_1',
            'in37': 'in37_A5_M211_stage_2',
            'in38': 'in38_A6_M211_ccw',
            'in39': 'in39_A7_M211_cw',
            'in40': 'in40_A8_spindle_break',
            'in41': 'in41_A9_prepare_toolchange',
            'in42': 'in42_A10_unclamp_3rd_axis',
            'in43': 'in43_A11_clamp_4th_axis',
            'in44': 'in44_A12_feed_driver',
            'in45': 'in45_A13_door_lock',
            'in46': 'in46_A14_confirm',
            'in47': 'in47_A15_free',
            'in48': 'in48_A16_block_1_forward',
            'in49': 'in49_A17_block_1_backward',
            'in50': 'in50_A18_block_2_forward',
            'in51': 'in51_A19_block_2_backward',
            'in52': 'in52_A20_block_3_forward',
            'in53': 'in53_A21_block_3_backward',
            'in54': 'in54_A22_axis_1_approve',
            'in55': 'in55_A23_axis_2_approve',
            'in56': 'in56_A24_axis_3_approve',
            'in57': 'in57_A25_axis_4_approve',
            'in58': 'in58_A26_free',
            'in59': 'in59_A27_free',
            'in60': 'in60_A28_free',
            'in61': 'in61_A29_free',
            'in62': 'in62_A30_free',
            'in63': 'in63_A31_emergency_stop',
        }, inplace=True)

        if len(time_interval):
            record = record[(record['Time'] > time_interval[0]) & (record['Time'] < time_interval[1])]
            record_tail = record.tail(1).copy()
            record_tail['Time'] = time_interval[1]
            record_head = record.head(1).copy()
            record_head['Time'] = time_interval[0]
            record = pd.concat([record_head, record, record_tail]).reset_index(drop = True)
            print(record.head())


        record *= 0.8
        record["Time"] /= 0.8

        i = 0
        y_string = []
        for column in record:
            if(i):
                if(filter == '' and len(args) == 0):
                    record[column] += (i-1)
                    y_string.append(column)
                    i += 1
                elif(filter == 'zero' and record[column].max()):
                    record[column] += (i-1)
                    y_string.append(column)
                    i += 1
                elif(filter == 'constant' and record[column].max() != record[column].min()):
                    record[column] += (i-1)
                    y_string.append(column)
                    i += 1
                elif(column in column_list):
                    record[column] += (i-1)
                    y_string.append(column)
                    i += 1
            else:
                i += 1

        if(len(y_string)):
            y_ticks = []
            for i in range(0, len(y_string)):
                y_ticks.append(i+0.4)

            fig = plt.figure(figsize=(20, 10))
            ax = plt.subplot2grid((1, 8), (0, 0), colspan=8)
            record.plot(x="Time", y=y_string, ax=ax)
            ax.grid(True, axis='y')

            ax.set_yticks(y_ticks)
            ax.set_yticklabels(y_string)
            ax.get_legend().remove()
            plt.title(filename)
            plt.xlabel('Time [s]')
            plt.subplots_adjust(top=0.95, bottom=0.05, right=0.95, left=0.15)

            if save:
                name = filename.split(".")
                plt.savefig(name[0] + '.' + save, dpi=150)
            else:
                plt.show()
        else:
            print "Nothing to plot!"
