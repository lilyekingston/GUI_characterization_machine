import matlab.engine
import time
import nidaqmx
import re

def readdaq():
    task = nidaqmx.Task()
    task.ai_channels.add_ai_voltage_chan("Dev2/ai0")
    task.start
    values = task.read()
    task.stop()
    task.close()
    return values


# Starts matlab engine
eng = matlab.engine.start_matlab()

print("Initializing...\n")

# Initializes motor slide
Arduino = eng.StepCommandInitializeArduino()
Shield = eng.StepCommandInitializeShield(Arduino)
Motor = eng.StepCommandInitializeMotor(Arduino, Shield)

print("Reading test profile...\n")





# Open the text file and read its contents
with open("example.txt", "r") as f:
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
    CurrentForce = readdaq() # Needs to read from capacitive sensor
    CurrentTime = int(time.time()-t_start)
    while Counter < abs(Limit) and CurrentForce < ForceLimit and CurrentTime < TimeLimit:
        eng.StepCommand(dx,Motor) # Moves the slide +/- 1mm each time it's called. +/- is controlled by the sign of dx.
        Counter = Counter + 1
        Values = readdaq() # Grabs from analog channels on DAQ
        CurrentForce = Values # Needs to read from capacitive sensor channel
        CurrentTime = int(time.time()-t_start)

# Releases the motor and arduino
eng.StepCommandRelease(Arduino,Motor)