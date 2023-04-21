import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import threading
import time
import multiprocessing as mp
import PySimpleGUI as sg

import nidaqmx
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image 
from io import BytesIO
import numpy as np
import matplotlib.figure as figure
from threading import Thread
import threading
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
matplotlib.use('TkAgg') 
import matplotlib.gridspec as gridspec

fig = figure.Figure()

def plot_data(xs, ys, channels, y_range, x_len, num_rows, num_cols):
    fig = plt.figure(figsize=(12, 8)) 
    gs = gridspec.GridSpec(num_rows, num_cols, figure,hspace=0.25)
    axes =[]
    lines = []
    for i in range(len(channels)):
        ys.append([0] * x_len)
        ax = fig.add_subplot(gs[i], aspect='auto')
        ax.set_ylim(y_range)
        line, = ax.plot(xs, ys[i])
        if i == 0:
            ax.set_title('Force from Load Cell Reading')
        elif i == 1:
            ax.set_title('Resistance from Wheatstone Bridge')
        else:
            ax.set_title('Voltage for channel ' + str(i))
        ax.set_xlabel('t [s]')
        ax.set_ylabel('Voltage [V]')
        ax.grid()
        axes.append(ax)
        lines.append(line)
    
    return fig, axes

#def plot_data(xs, ys, channels, y_range, x_len):
#    figs = []
#    axes = []
#    lines = []
#    #figs, axes = plt.subplots(2, 2, figsize=(92,6), layout='constrained', sharex=True)
#    #figs.suptitle('Channel Data')
#    for i  in range(len(channels)):
#        ys.append([0] * x_len)
#        figs.append(plt.figure())
#        axes.append(figs[i].add_subplot(1, 1, 1))
#        axes[i].set_ylim(y_range)
#        line, = axes[i].plot(xs, ys[i])
#        if i == 0:
#            #axes[i].set_title('Force from Load Cell Reading')
#            plt.title('Force from Load Cell Reading')
#        elif i == 1:
#            #axes[i].set_title('Resistance from Wheatstone Bridge')
#            plt.title('Resistance from Wheatstone Bridge')
#        elif i == 3:
#            #axes[i].set_title('Resistance from Wheatstone Bridge')
#            plt.title('Resistance from Wheatstone Bridge')
#        else:
#            #axes[i].set_title('Voltage for channel' + str(i))
#            plt.title('Voltage for channel' + str(i))
#        axes[i].set_xlabel('t [s]')
#        axes[i].set_ylabel('Voltage [V]')
#        axes[i].grid()
#        lines.append(line)
        
#    return figs



k=0

   
# List of channels to read from 
num_channels = 10
resis_chan = ["Dev3/ai1", "Dev3/ai5", "Dev3/ai6", "Dev3/ai7", "Dev3/ai8", "Dev3/ai9", "Dev3/ai10"]
# Voltage to newtons conversion factor 
voltage_to_newtons = (1/10) * 1.25

# Resistance values 
R1 = 100
R3 = 100
R2 = 1000


hardware_name = sg.popup_get_text('Enter hardware name for your DAQ Device', title='Hardware Selection')

hardware_str = str(hardware_name)
# Create list of channels to read from
channels = []
for i in range(num_channels):
    channels.append(hardware_str + str(i))

    
# Read from DAQ device
def readdaq():
    global ForceValue
    task = nidaqmx.Task()
    # add channels to task using a loop
    for channel in channels:
        task.ai_channels.add_ai_voltage_chan(channel)
    task.start()
    values = task.read() # read values
    task.stop()
    task.close()

    # Convert voltages for ai0 to newtons
    values[0] = (10*values[0])/0.6
    values[0] = (values[0] / 10) * 1.25
    ForceValue = values[0]
    #print(values)
    v_source = 4.71 # source voltage average
    # Convert voltage to resistance for other channels 
    value_clean = [values[0], [], values[2], values[3]]
    channels_clean = [channels[0], [], channels[2], channels[3]]
    for i in range(1,10):
        if i == 1 or (i >= 4 and i <= 10):
            if values[i] > 2:
                values[i] = (R2 * (R3 * (v_source - values[i]) - (R1 * values[i]))) / (R1 * (v_source + values[i]) + (R3 * values[i]))
                value_clean[1] = (R2 * (R3 * (v_source - values[i]) - (R1 * values[i]))) / (R1 * (v_source + values[i]) + (R3 * values[i]))
                channels_clean.append(channels[i])
            elif 0 <= values[i] < 2:
                values[i] = 0
            else:
                values[i] = 0
            return value_clean, channels_clean
        

    return value_clean, channels_clean # Return values from all channels
    
channels_clean = readdaq()[1]

    
def writefiledata(t, values):
    # Open file
    with open("Result.txt", 'a') as file:
        time = str(t)
        values_str = [str(v) for v in values]
        values_line = "\t".join([time] + values_str) + "\n"
        file.write(values_line)
    # Close file
    file.close()
    
 
Ts = 0.01 # Sampling time [seconds]
N = 100
k =1
x_len = N # Number of points to display
Ymin = -10; Ymax = 10
y_range = [Ymin, Ymax] # Range of possible Y values to display

    
# Create figure for plotting
figs = []
axes = []
xs = list(range(0, N))
# Create list for each channel
ys = []
lines = []

k=0
logging_stop = False

def logging(i):
    global logging_stop
    if logging_stop == False:
        #newvalues = readdaq()[1] # Read values from all channels
        result = readdaq()
        valuesdata = result[0]
        #global value_clean
        valuesrounded = [round(v, 3) if isinstance(v, (int, float)) else v for v in valuesdata] # Round values to limit file size
        #print("values =", valuesrounded) # Debug print, delete this later
        time.sleep(Ts)
        global k 
        k += 1
        Timer = round(k*Ts, 3)
        writefiledata(Timer, valuesrounded) # Write data for all channels to file
        for j, line in enumerate(lines):
            ys[j].append(valuesrounded[j]) # Add y to list for each channel
            ys[j] = ys[j][-x_len:] # Limit y list to set number of items for each channel
            line.set_ydata(ys[j]) # Update line with new Y values for each channel
            axes[j].relim()
            axes[j].autoscale_view()
        return lines
# Get figure and axes from plot_data() function

#fig = plt.figure()
#canvas = FigureCanvasTkAgg(fig, master=sg.Window('Channel Data').TKroot)

figs, axes = plot_data(xs=xs, ys=ys, channels=channels_clean, y_range=y_range, x_len=x_len, num_rows = 2, num_cols=2)

# Create animation
ani = animation.FuncAnimation(figs, logging, interval=10, blit=True, cache_frame_data=False)



plt.show()
    