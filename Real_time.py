import serial
import pandas as pd
import numpy as np
import joblib
import tkinter as tk
from tkinter import StringVar
from collections import Counter

# Column names for the dataframe
column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']
df = pd.DataFrame(columns=column_names)

# Serial port configuration
serial_port = 'COM4'
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate, timeout=0.01)

# Load the trained model
loaded_model = joblib.load('Trained_model/knn_model.pkl')

# Labels for predictions
labels = ["UP","DOWN","LEFT","RIGHT","CLOCKWISE","REST","FORWARD","BACKWARD"]

# Tkinter GUI setup
root = tk.Tk()
root.title("Hand Gesture Prediction")
root.geometry("300x100")

# Variable to display prediction
predicted_label = StringVar()
predicted_label.set("Waiting for prediction...")

# Label widget to show the prediction
label = tk.Label(root, textvariable=predicted_label, font=("Helvetica", 16))
label.pack(pady=20)

# Sliding window parameters
y = 0
x = len(df)
prediction_buffer = []  # Buffer to store last 5 predictions

# Function to determine majority prediction
def get_majority_vote(buffer):
    if len(buffer) < 5:
        return "Waiting..."
    counter = Counter(buffer)
    most_common = counter.most_common(1)
    if most_common[0][1] > 2:  # Majority exists (more than 2 occurrences)
        return labels[most_common[0][0]]
    else:
        return "Noise"

# Function to process incoming serial data
def process_data():
    global x, y, df, prediction_buffer

    if ser.in_waiting > 0:  # Check if data is available in the serial buffer
        data = ser.readline().decode('utf-8')
        if data:
            try:
                # Parse data and append to dataframe
                row = data.split(",")
                df.loc[x] = row[1:7]
                x += 1
            except ValueError:
                print("Value error: Could not parse row")

    # Process data if at least 400 rows are available
    if x > 400:
        if y + 400 <= x:
            # Extract the sliding window and normalize data
            window = df.iloc[y:y + 400].apply(pd.to_numeric, errors='coerce').values.astype(np.float32)
            window = (window - window.min(axis=0)) / (window.max(axis=0) - window.min(axis=0))
            window = window.flatten()

            # Predict gesture
            try:
                prediction = loaded_model.predict(window.reshape(1, -1))
                prediction_buffer.append(int(prediction[0]))  # Append to buffer
                if len(prediction_buffer) > 5:  # Maintain buffer size
                    prediction_buffer.pop(0)
                # Determine majority prediction and update GUI
                majority_prediction = get_majority_vote(prediction_buffer)
                predicted_label.set(f"Prediction: {majority_prediction}")
            except Exception as e:
                print(f"Prediction error: {e}")
                predicted_label.set("Error in prediction")
            
            # Slide the window
            y += 10
        else:
            print("Waiting for more data to process sliding window")

    # Repeat this function
    root.after(10, process_data)

# Start the GUI and data processing loop
if ser.is_open:
    print(f"Connected to {serial_port} at {baud_rate} baud")
    root.after(10, process_data)
    root.mainloop()
else:
    print(f"Failed to open serial port {serial_port}")
