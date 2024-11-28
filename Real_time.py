import serial
import time
import pandas as pd
from glob import glob
import sys
import numpy as np
import joblib

column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']
df = pd.DataFrame(columns=column_names)


serial_port = 'COM4'  
baud_rate = 115200 
ser = serial.Serial(serial_port, baud_rate, timeout=0.01)

labels = ["UP","DOWN","LEFT","RIGHT","ANTICLOCKWISE","CLOCKWISE"]

if ser.is_open:
    print(f"Connected to {serial_port} at {baud_rate} baud")
    #print(f"Storing data for {gesture} gesture in {filename}")

loaded_model = joblib.load('Trained_model/svm_model.pkl')

y = 0
x = len(df)
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

        if x>400:
            if y+400<x:
                # df[['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']] = df[
                #     ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']
                # ].apply(pd.to_numeric, errors='coerce')
                
                window = df.iloc[y:y+400]
                window = window.apply(pd.to_numeric, errors='coerce')
                window = window.values.astype(np.float32)
                window = (window - window.min(axis=0)) / (window.max(axis=0) - window.min(axis=0))
                window = window.flatten()

                predictions=loaded_model.predict(window.reshape(1,-1))
                print(labels[predictions[0]])
                y+=10
            else:
                print("Waiting for more data for sliding data")

        print("Waiting for the first 4 secs")


