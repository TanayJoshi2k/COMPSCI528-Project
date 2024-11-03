import serial
import time
import pandas as pd
from glob import glob
import sys

column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']
df = pd.DataFrame(columns=column_names)


serial_port = 'COM4'  
baud_rate = 115200 
ser = serial.Serial(serial_port, baud_rate, timeout=1)

gestures = ["UP","DOWN","LEFT","RIGHT"]
#gesture = int(input("Enter the gesture type (1:UP/2:DOWN/3:LEFT/4:RIGHT): "))

gesture = int(sys.argv[1])



if ser.is_open:
    print(f"Connected to {serial_port} at {baud_rate} baud")
    #print(f"Storing data for {gesture} gesture in {filename}")


#all_data = []
x = len(df)
try:  
    while True:  
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
            time.sleep(0.01)         
        


except KeyboardInterrupt:  
    print("Stopping data collection")




finally:
    # with open(filename, 'a') as file:
    #     for line in all_data:
    #         file.write(line + '\n') 

    files = glob(f"Data/{gestures[gesture-1]}_*")
    filename = f"Data/{gestures[gesture-1]}_gesture_data_{len(files)+1}.csv"
    df.to_csv(filename)
    print(f"Data written to {filename}")


    
    ser.close()
    print("Serial connection closed")