import serial
import time
import pandas as pd
from glob import glob
import sys
import matplotlib.pyplot as plt
import numpy as np

column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']
df = pd.DataFrame(columns=column_names)


serial_port = 'COM4'  
baud_rate = 115200 
ser = serial.Serial(serial_port, baud_rate, timeout=0.01)

gestures = ["UP","DOWN","LEFT","RIGHT","NEW_CLOCKWISE","REST","FORWARD","BACKWARD"]
#gesture = int(input("Enter the gesture type (1:UP/2:DOWN/3:LEFT/4:RIGHT): "))

gesture = int(sys.argv[1])



if ser.is_open:
    print(f"Connected to {serial_port} at {baud_rate} baud")
    #print(f"Storing data for {gesture} gesture in {filename}")


#all_data = []
# x = len(df)
# try:  
#     while True:  
#         if ser.in_waiting > 0: 
#             data = ser.readline().decode('utf-8')#.rstrip() 
#             if data:
#                 print(f"Received: {data}")
#                 try:
#                     row = data.split(",")
#                     #print(row)
#                     df.loc[x] = row[1:7]
#                     x+=1
#                 except ValueError:
#                     print("Value error")
#             #time.sleep(0.01)         
        


# except KeyboardInterrupt:  
#     print("Stopping data collection")




# finally:
#     # with open(filename, 'a') as file:
#     #     for line in all_data:
#     #         file.write(line + '\n') 

#     files = glob(f"Data/{gestures[gesture-1]}_*")
#     filename = f"Data/{gestures[gesture-1]}_gesture_data_{len(files)+1}.csv"
#     df.to_csv(filename)
#     print(f"Data written to {filename}")


    
#     ser.close()
#     print("Serial connection closed")

all_data = []
x = len(df)
while x<=400:  
    if ser.in_waiting > 0: 
        data = ser.readline().decode('utf-8')#.rstrip() 
        if data:
            print(f"Received: {data}")
            try:
                row = data.split(",")
                #print(row)
                df.loc[x] = row[1:7]
                x+=1
            except ValueError:
                print("Value error")
        #time.sleep(0.01)     

# with open(filename, 'a') as file:
#     for line in all_data:
#         file.write(line + '\n') 

def spectrogram_and_plot(data):
    for col in ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']:
        data[col] = pd.to_numeric(data[col], errors='coerce')
    # Extract individual sensor data (gyro and accelerometer)
    gyro_x = data['gyro_x'].values
    gyro_y = data['gyro_y'].values
    gyro_z = data['gyro_z'].values
    acce_x = data['acce_x'].values
    acce_y = data['acce_y'].values
    acce_z = data['acce_z'].values

    # Number of samples (N) and sampling interval (T)
    N = len(gyro_x)  # Assuming all columns have the same number of samples
    T = 1/100  # Replace with the actual sampling rate (T = 1 / sampling frequency)
    fs = 1/T

    # Plotting the time-domain data for gyroscope and accelerometer
    plt.figure(figsize=(12, 20))

    # Plot Gyroscope time-domain data
    plt.subplot(2, 1, 1)
    plt.plot(np.arange(N) * T, gyro_x, label='Gyro X')
    plt.plot(np.arange(N) * T, gyro_y, label='Gyro Y')
    plt.plot(np.arange(N) * T, gyro_z, label='Gyro Z')
    plt.title('Time Domain - Gyroscope Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()

    # Plot Accelerometer time-domain data
    plt.subplot(2, 1, 2)
    plt.plot(np.arange(N) * T, acce_x, label='Acce X')
    plt.plot(np.arange(N) * T, acce_y, label='Acce Y')
    plt.plot(np.arange(N) * T, acce_z, label='Acce Z')
    plt.title('Time Domain - Accelerometer Data')
    plt.xlabel('Time (s)')
    plt.ylabel('Amplitude')
    plt.legend()
    plt.grid()

    plt.tight_layout()    
    plt.show()

files = glob(f"Data/{gestures[gesture-1]}_gesture_*")
filename = f"Data/{gestures[gesture-1]}_gesture_data_{len(files)+1}.csv"
df.to_csv(filename)
print(f"Data written to {filename}")

ser.close()
print("Serial connection closed")

#spectrogram_and_plot(df)