
from curses import can_change_color
import PySimpleGUI as sg
import pathlib as Path
import os.path
from os import path 
import nidaqmx
import time
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from PIL import Image 
from io import BytesIO
import base64
import numpy as np
import matplotlib.figure as figure
import AlliedVision
from threading import Thread
import threading
import matlab.engine
import re
#from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib
#matplotlib.use('TkAgg') 
import cv2


ForceValue = 0

sg.theme('DarkBlue2')   # Add a touch of color

# pathname for Lab logo image
pathname = r"C:\Users\lilye\OneDrive\Desktop\smslogo.png"

# Columns for frame of steps 
col1 = [[sg.Frame("Step 1", [               [sg.Text(font=("Arial", 11), key='-STEP-')], 
                                            [sg.Text(font=("Arial", 11), key='-1STEP1-')],
                                            [sg.Text(font=("Arial", 11), key='-1STEP2-')],
                                            [sg.Text(font=("Arial", 11), key='-1STEP3-')],
                                            [sg.Text(font=("Arial", 11), key='-1STEP4-')]], 
                                                size=(100, 170) ) ]]
col2 = [[sg.Frame("Step 2", [               [sg.Text(font=("Arial", 11), key='-1STEP5-')],
                                            [sg.Text(font=("Arial", 11), key='-2STEP0-')], 
                                            [sg.Text(font=("Arial", 11), key='-2STEP1-')],
                                            [sg.Text(font=("Arial", 11), key='-2STEP2-')],
                                            [sg.Text(font=("Arial", 11), key='-2STEP3-')]],
                                                size=(100, 170) ) ]]
col3 = [[sg.Frame("Step 3", [               [sg.Text(font=("Arial", 11), key='-2STEP4-')], 
                                            [sg.Text(font=("Arial", 11), key='-2STEP5-')],
                                            [sg.Text(font=("Arial", 11), key='-3STEP0-')],
                                            [sg.Text(font=("Arial", 11), key='-3STEP1-')],
                                            [sg.Text(font=("Arial", 11), key='-3STEP2-')]],
                                                size=(100, 170) ) ]]
col4 = [[sg.Frame("Step 4", [               [sg.Text(font=("Arial", 11), key='-3STEP4-')], 
                                            [sg.Text(font=("Arial", 11), key='-3STEP5-')],
                                            [sg.Text(font=("Arial", 11), key='-4STEP0-')],
                                            [sg.Text(font=("Arial", 11), key='-4STEP1-')],
                                            [sg.Text(font=("Arial", 11), key='-4STEP2-')]],
                                                size=(100, 170) ) ]]

# Laying out tab elements for default values bar. 


# All the stuff inside your window.
layout1 = [  
            [sg.Text('SMS Pro 1 Software', font=('any 50'))], # size() with text puts spacing around the text
            [sg.Text('Current status: '), sg.Text(size=(55,1), key='-STATUS-')],
            [sg.Text('Current profile: '), sg.Text(size=(55,1), key='-PROFILE-')],
            [sg.Button('Start Test',size = (20,3)), sg.Button('Stop Test',size = (20,3))], # size() changes the size of the buttons
            [sg.Button('Read',size = (20,3)), sg.Text('File path:'), sg.Input(key='-IN-'),sg.FileBrowse(key='-IN-', enable_events=True, file_types=(('TXT File', '*.txt'),))],
            [sg.Button('Build Profile', size=(20,3))],
            [sg.Column(col1, element_justification='c'), sg.Column(col2, element_justification='c')
                        , sg.Column(col3, element_justification='c'), sg.Column(col4, element_justification='c')]
          
            ] 

# Side bar layout for common value tabs
layout2 = [ [sg.Text('Useful information for \nusing SMS Pro 1 Software:', font=('any 15'))],
            [sg. Text('When starting the test, you must enter the \nname under which the data acquisition \ndevice exists in your computer.\nThis might look something like: Dev1/ai', font=('any 10'))]
           ]

# Combining layouts for full
layout = [[[sg.Image(filename=r'C:\Users\lilye\OneDrive\Desktop\smslogoo.png', size=(900,200))],
    [sg.Column(layout1),
        sg.VSeperator(),
        sg.Column(layout2),]]
]
# Create the Window
window = sg.Window('GUI', layout, resizable=True, finalize=True, size=(950,850)) # Needs finalize=True for window.maximize() to work
window['-STATUS-'].update('No profile selected')


fig = figure.Figure()

def longfunct_thread(window):
    window.write_event_value('-THREAD-', "Logs Saved Successfully")
    time.sleep(10)
    window.write_event_value('-THREAD DONE-', 'done')


 
def display_daq():
    os.system('python mod2.py')

    

def cameras(): 
    os.system('python AlliedVision.py')



# Function for motor slide integrated into GUI
def motorslide(): 
    # Starts matlab engine
    eng = matlab.engine.start_matlab()

    print('Initializing...\n')

    # Initializes motor slide
    Arduino = eng.StepCommandInitializeArduino()
    Shield = eng.StepCommandInitializeShield()
    Motor = eng.StepCommandInitializeMotor(Arduino, Shield)

    print('Reading test profile...\n')

    # Open the text file and read its contents
    with open("steps.txt", "r") as f:
        contents = f.read()

    # Split the contents into individual lines
    lines = contents.split("\n")

    # Initialize arrays to hold the values we're interested in
    Steps = []
    Distance = []
    Force = []
    Time = []

    # Regular expressions to match parameter lines
    speed_re = re.compile(r"Speed ([0-9]+) (.+)")
    load_re = re.compile(r"Load ([0-9]+) (.+)")
    extension_re = re.compile(r"Extension ([0-9]+) (.+)")
    time_re = re.compile(r"Time ([0-9]+) (.+)")

    # Loop through each line in the file
    for line in lines:
        # If this is a new step, record its number and initialize the arrays
        if line == "Actuate":
            step_num = len(Steps) + 1
            Steps.append(step_num)
            Distance.append(None)
            Force.append(None)
            Time.append(None)
        # If this is a distance parameter, record its value
        elif "Extension" in line:
            distance_str = line.split()[1]
            if distance_str != "N/A":
                distance_val = int(distance_str)
                Distance[-1] = distance_val
        # If this is a force parameter, record its value
        elif "Load" in line:
            load_match = load_re.match(line)
            if load_match is not None:
                load_val = int(load_match.group(1))
                Force[-1] = load_val
        # If this is a time parameter, record its value
        elif "Time" in line:
            time_match = time_re.match(line)
            if time_match is not None:
                time_val = int(time_match.group(1))
                Time[-1] = time_val

    Distance = [d if d is not None else 99 for d in Distance]
    Force = [f if f is not None else 99 for f in Force]
    Time = [t if t is not None else 99 for t in Time]

    # Print out the arrays for debugging purposes
    print("Test to perform:\n")
    print("Steps:", Steps)
    print("Distance:", Distance)
    print("Force:", Force)
    print("Time:", Time)



    #Steps = [1, 2] # Hard coded two steps for now
    #Distance = [-10,10] # Hard coded displacements for now
    #Force = [10,10] # Hard coded force limits for now
    #Time = [3,15] # Hard coded time limits for now



    # Loops for each step from the testing profile
    for i in range(len(Steps)):
        print("Starting step number: ", Steps[i])


        #dx = int(input('Input distance to move (mm): '))
        dx = Distance[i]
    
        Fmax = 1.25 # Maximum load
        Vmax = 10
        ForceLimit = 10*(Force[i]/Fmax) # N -> V
        if ForceLimit > Fmax:
            ForceLimit = Vmax

        TimeLimit = Time[i]

        t_start = time.time()
        CurrentTime = int(time.time()-t_start)


        Limit = dx
        Counter = 0
        CurrentForce = ForceValue # Needs to read from capacitive sensor
        CurrentTime = int(time.time()-t_start)
        while Counter < abs(Limit) and CurrentForce < ForceLimit and CurrentTime < TimeLimit:
            eng.StepCommand(dx,Motor) # Moves the slide +/- 1mm each time it's called. +/- is controlled by the sign of dx.
            Counter = Counter + 1
            Values = ForceValue # Grabs from analog channels on DAQ
            print(ForceValue)
            CurrentForce = Values # Needs to read from capacitive sensor channel
            CurrentTime = int(time.time()-t_start)

    # Releases the motor and arduino
    eng.StepCommandRelease(Arduino,Motor)


stopthread = False
def stop_test():
    os._exit(display_daq)
    os._exit(cameras)
   
  


ActionNames = ["Actuate", "Repeat","N/A"]
ParameterNames = ["Time", "Load", "Extension","N/A"]
DistanceParameterNames = ["Speed","N/A"]
DistanceParameterUnitNames = ["mm/s","cm/s","in/s"]
UnitNames = ["seconds",'N','lbf','kg','mm','cm','m','in','N/A']
def ProfileEditor():
    ProfileEditorlayout = [  [sg.Text('Profile Editor', font=('any 40'))],
                                [sg.Button('Close', key='-CLOSE-'), sg.Button('Click to save'),sg.Text('File name:'), sg.Input(key='-SAVE_FILENAME-')],
                                [sg.Text('Step 1:'),sg.DropDown(ActionNames,key='-STEP1-',default_value='Actuate')],
                                [sg.Text('Condition 1:'), sg.DropDown(ParameterNames,key='-P1-',size=(10,1),default_value='Extension'),sg.Text('Value:'),sg.Input(key='-P1VAL-', size=(5,1), default_text=5), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT1-',size=(10,1), default_value='mm')],
                                [sg.Text('Condition 2:'), sg.DropDown(ParameterNames,key='-P2-',size=(10,1),default_value='Load'),sg.Text('Value:'),sg.Input(key='-P2VAL-', size=(5,1), default_text=1), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT2-',size=(10,1), default_value='N')],
                                [sg.Text('Condition 3:'), sg.DropDown(ParameterNames,key='-P3-',size=(10,1),default_value='Time'),sg.Text('Value:'),sg.Input(key='-P3VAL-', size=(5,1), default_text=20), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT3-',size=(10,1), default_value='seconds')],
                                [sg.Text('Condition 4:'), sg.DropDown(ParameterNames,key='-P4-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P4VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT4-',size=(10,1))],
                                [sg.Text('Condition 5:'), sg.DropDown(ParameterNames,key='-P5-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P5VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT5-',size=(10,1))],
                                [sg.Text('Step 2:'),sg.DropDown(ActionNames,key='-STEP2-',default_value='Actuate')],
                                [sg.Text('Condition 1:'), sg.DropDown(ParameterNames,key='-P6-',size=(10,1),default_value='Extension'),sg.Text('Value:'),sg.Input(key='-P6VAL-', size=(5,1), default_text=-5), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT6-',size=(10,1), default_value='mm')],
                                [sg.Text('Condition 2:'), sg.DropDown(ParameterNames,key='-P7-',size=(10,1),default_value='Load'),sg.Text('Value:'),sg.Input(key='-P7VAL-', size=(5,1), default_text=1), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT7-',size=(10,1), default_value='N')],
                                [sg.Text('Condition 3:'), sg.DropDown(ParameterNames,key='-P8-',size=(10,1),default_value='Time'),sg.Text('Value:'),sg.Input(key='-P8VAL-', size=(5,1), default_text=20), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT8-',size=(10,1), default_value='seconds')],
                                [sg.Text('Condition 4:'), sg.DropDown(ParameterNames,key='-P9-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P9VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT9-',size=(10,1))],
                                [sg.Text('Condition 5:'), sg.DropDown(ParameterNames,key='-P10-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P10VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT10-',size=(10,1))],
                                [sg.Text('Step 3:'),sg.DropDown(ActionNames,key='-STEP3-',default_value='N/A')],
                                [sg.Text('Condition 1:'), sg.DropDown(ParameterNames,key='-P11-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P11VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT11-',size=(10,1))],
                                [sg.Text('Condition 2:'), sg.DropDown(ParameterNames,key='-P12-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P12VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT12-',size=(10,1))],
                                [sg.Text('Condition 3:'), sg.DropDown(ParameterNames,key='-P13-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P13VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT13-',size=(10,1))],
                                [sg.Text('Condition 4:'), sg.DropDown(ParameterNames,key='-P14-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P14VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT14-',size=(10,1))],
                                [sg.Text('Condition 5:'), sg.DropDown(ParameterNames,key='-P15-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P15VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT15-',size=(10,1))],
                                [sg.Text('Step 4:'),sg.DropDown(ActionNames,key='-STEP4-',default_value='N/A')],
                                [sg.Text('Condition 1:'), sg.DropDown(ParameterNames,key='-P16-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P16VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT16-',size=(10,1))],
                                [sg.Text('Condition 2:'), sg.DropDown(ParameterNames,key='-P17-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P17VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT17-',size=(10,1))],
                                [sg.Text('Condition 3:'), sg.DropDown(ParameterNames,key='-P18-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P18VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT18-',size=(10,1))],
                                [sg.Text('Condition 4:'), sg.DropDown(ParameterNames,key='-P19-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P19VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT19-',size=(10,1))],
                                [sg.Text('Condition 5:'), sg.DropDown(ParameterNames,key='-P20-',size=(10,1),default_value='N/A'),sg.Text('Value:'),sg.Input(key='-P20VAL-', size=(5,1)), sg.Text('Unit:'), sg.DropDown(UnitNames,key='-UNIT20-',size=(10,1))]]


    ProfileEditorWindow = sg.Window('Profile Editor', ProfileEditorlayout, size=(500,900), finalize=True)

    while True:
        event, values = ProfileEditorWindow.read()
        if event in (sg.WIN_CLOSED, '-CLOSE-'):
            window['-STATUS-'].update('Editor closed, select a profile')
            ProfileEditorWindow.close()
            break
        if event == 'Click to save':
            SaveFilename = values['-SAVE_FILENAME-']
            f = open(SaveFilename+'.txt','x')
            lines = [[str(values['-STEP1-'])],
            [str(values['-P1-'])+' '+str(values['-P1VAL-'])+' '+str(values['-UNIT1-'])],
            [str(values['-P2-'])+' '+str(values['-P2VAL-'])+' '+str(values['-UNIT2-'])],
            [str(values['-P3-'])+' '+str(values['-P3VAL-'])+' '+str(values['-UNIT3-'])],
            [str(values['-P4-'])+' '+str(values['-P4VAL-'])+' '+str(values['-UNIT4-'])],
            [str(values['-P5-'])+' '+str(values['-P5VAL-'])+' '+str(values['-UNIT5-'])],
            [str(values['-STEP2-'])],
            [str(values['-P6-'])+' '+str(values['-P6VAL-'])+' '+str(values['-UNIT6-'])],
            [str(values['-P7-'])+' '+str(values['-P7VAL-'])+' '+str(values['-UNIT7-'])],
            [str(values['-P8-'])+' '+str(values['-P8VAL-'])+' '+str(values['-UNIT8-'])],
            [str(values['-P9-'])+' '+str(values['-P9VAL-'])+' '+str(values['-UNIT9-'])],
            [str(values['-P10-'])+' '+str(values['-P10VAL-'])+' '+str(values['-UNIT10-'])],
            [str(values['-STEP3-'])],
            [str(values['-P11-'])+' '+str(values['-P11VAL-'])+' '+str(values['-UNIT11-'])],
            [str(values['-P12-'])+' '+str(values['-P12VAL-'])+' '+str(values['-UNIT12-'])],
            [str(values['-P13-'])+' '+str(values['-P13VAL-'])+' '+str(values['-UNIT13-'])],
            [str(values['-P14-'])+' '+str(values['-P14VAL-'])+' '+str(values['-UNIT14-'])],
            [str(values['-P15-'])+' '+str(values['-P15VAL-'])+' '+str(values['-UNIT15-'])],
            [str(values['-STEP4-'])],
            [str(values['-P16-'])+' '+str(values['-P16VAL-'])+' '+str(values['-UNIT16-'])],
            [str(values['-P17-'])+' '+str(values['-P17VAL-'])+' '+str(values['-UNIT17-'])],
            [str(values['-P18-'])+' '+str(values['-P18VAL-'])+' '+str(values['-UNIT18-'])],
            [str(values['-P19-'])+' '+str(values['-P19VAL-'])+' '+str(values['-UNIT19-'])],
            [str(values['-P20-'])+' '+str(values['-P20VAL-'])+' '+str(values['-UNIT20-'])]]

            for i in range(0,len(lines),1):
                WriteVar = lines[i]
                f.writelines(WriteVar)
                f.writelines('\n')
            f.close()

    ProfileEditorWindow.close()


stopdaq = False

def update_gui(window, status):
    window.write_event_value('-UPDATE-', status)

while True:
    event, values = window.read()
    if event == sg.WIN_CLOSED or event == 'Cancel': 
        window.close() # if user closes window or clicks cancel
        break
    elif event == '-THREAD-':
        sg.popup_notify("Logs Saved Successfully")
    elif event == '-THREAD DONE-':
        # Handle thread done event
        pass
    if event == 'Read':
        print('Current path: ', values)
        window['-PROFILE-'].update(values['-IN-'])
        window['-STATUS-'].update('Profile selected')
        filename = values['-IN-']
        if path.exists(filename):  # if the file exists they chose
            try: 
                with open(filename, "r") as f:   # then program will open and read filename saved as text and print the .txt file
                    text = f.read().splitlines()
                    print(text)
                    window['-STEP-'].update(text[0])
                    window['-1STEP1-'].update(text[1])
                    window['-1STEP2-'].update(text[2])
                    window['-1STEP3-'].update(text[3])
                    window['-1STEP4-'].update(text[4])
                    window['-1STEP5-'].update(text[5])
                    window['-2STEP0-'].update(text[6])
                    window['-2STEP1-'].update(text[7])
                    window['-2STEP2-'].update(text[8])
                    window['-2STEP3-'].update(text[9])
                    window['-2STEP4-'].update(text[10])
                    window['-2STEP5-'].update(text[11])
                    window['-3STEP0-'].update(text[12])
                    window['-3STEP1-'].update(text[13])
                    window['-3STEP2-'].update(text[14])
                    window['-3STEP4-'].update(text[16])
                    window['-3STEP5-'].update(text[17])
                    window['-4STEP0-'].update(text[18])
                    window['-4STEP1-'].update(text[19])
                    window['-4STEP2-'].update(text[20])
                with open('steps.txt', 'w') as stepsfile:
                        stepsfile.write(str(text))
                        stepsfile.close()

            except Exception as e: 
                print("Error: ", e)
    if event == 'Start Test':
        window['-STATUS-'].update('Starting test...')
        
        threading.Thread(target=display_daq).start()
        threading.Thread(target=cameras).start()
        threading.Thread(target=motorslide).start()
        
    if event == 'Stop Test':
        window['-STATUS-'].update('Test stopped...')
        stop_test()

    if event == 'Build Profile':
        window['-STATUS-'].update('Profile editor opened')
        window['-PROFILE-'].update('Profile cleared')
        ProfileEditor()
          