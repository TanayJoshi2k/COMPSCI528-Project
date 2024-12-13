import serial
import pandas as pd
import joblib
import tkinter as tk
from tkinter import StringVar
import re
import numpy as np
import time

# Column names for the dataframe
column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']

# Serial port configuration
serial_port = 'COM4'
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate, timeout=0.01)

# Load the trained model
loaded_model = joblib.load('Trained_model/xgboost_model.pkl')

# Labels for predictions
labels = ["UP","DOWN","LEFT","RIGHT","REST","FORWARD","BACKWARD","NEW_CLOCKWISE"]
#labels = ["UP","DOWN","LEFT","RIGHT","REST"]

# Tkinter GUI setup
# root = tk.Tk()
# root.title("Hand Gesture Prediction")
# root.geometry("300x100")

# Variable to display prediction
# predicted_label = StringVar()
# predicted_label.set("Waiting for prediction...")

# Sliding window parameters
window_size = 400  # Number of rows for prediction
df = pd.DataFrame(columns=column_names)

def read_sensor_data(ser):
    """
    Read and process data from the serial port, returning the processed data as a list of floats.
    """
    try:
        data = ser.readline().decode('utf-8').strip()
        row = data.split(",")
        if len(row) >= 7:  # Ensure there are enough elements in the row
            # Clean the numeric values to handle garbage characters
            cleaned_row = [re.sub(r'[^\d.-]', '', value) for value in row[1:7]]
            #print(row,cleaned_row)
            return list(map(float, cleaned_row))  # Return cleaned data as a list of floats
    except Exception as e:
        print(f"Error processing sensor data: {e}")
    return None

def preprocess_data_for_inference(df, fixed_length=400):
    """
    Preprocess sensor data for inference to match training preprocessing steps.
    Normalize, pad/truncate to fixed_length, and flatten.
    """
    if not df.empty:
        # Select required columns and convert to NumPy array
        data = df[['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']].values.astype(np.float32)
        
        # Normalize data
        #data = (data - data.min(axis=0)) / (data.max(axis=0) - data.min(axis=0) + 1e-8)  # Avoid division by zero
        data = (data - data.mean(axis=0))

        # Adjust data length
        if len(data) > fixed_length:
            data = data[:fixed_length]  # Truncate if longer than fixed length
        elif len(data) < fixed_length:
            padding = np.zeros((fixed_length - len(data), data.shape[1]), dtype=np.float32)
            data = np.vstack((data, padding))  # Pad with zeros if shorter than fixed length

        # Flatten the data for model input
        return data.flatten().reshape(1, -1)
    else:
        raise ValueError("DataFrame is empty. Cannot preprocess for inference.")


def predict_gesture(data_frame, confidence_threshold=0.00):
    """
    Predict the gesture based on the collected data.
    Preprocess data to match the training format before prediction.
    Only select the label if confidence exceeds the threshold.
    """
    try:
        # Preprocess the data
        features = preprocess_data_for_inference(data_frame)

        # Predict probabilities for each class
        probabilities = loaded_model.predict_proba(features)[0]
        max_prob = max(probabilities)
        predicted_class = probabilities.argmax()

        # Check confidence threshold
        if max_prob >= confidence_threshold:
            return labels[predicted_class], max_prob
        else:
            return "Noise", max_prob
    except ValueError as e:
        print(f"Prediction error: {e}")
        return "Noise", 0.0
    except Exception as e:
        print(f"Unexpected error during prediction: {e}")
        return "Noise", 0.0



def main_loop():
    """Main loop for data collection, preprocessing, prediction, and GUI updates."""
    global df
    collecting = True  # Flag to control data collection
    types = 0
    while True:
        if collecting:
            # Collect data until we have 400 rows
            sensor_data = read_sensor_data(ser)
            if sensor_data:
                df.loc[len(df)] = sensor_data  # Append new row to DataFrame
                if len(df) == window_size:
                    # Stop collecting and switch to prediction
                    collecting = False
                    try:
                        # Predict gesture with confidence
                        prediction, confidence = predict_gesture(df)
                        #predicted_label.set(f"{prediction} ({confidence*100:.1f}%)")  # Update GUI with prediction
                        print(f"Predicted Gesture: {prediction} with Confidence: {confidence*100:.1f}%")
                        df.to_csv(f"Testing/{types}_{prediction}.csv")
                        types+=1
                    except Exception as e:
                        #predicted_label.set("Error")
                        print(f"Prediction error: {e}")
        else:
            # Reset for the next round of data collection
            collecting = True
            df = pd.DataFrame(columns=column_names)  # Clear the buffer
            #predicted_label.set("Waiting for prediction...")  # Reset GUI display
            time.sleep(1)

        # Update the GUI to reflect changes
        #root.update_idletasks()
        #root.update()



# Run the main loop
try:
    main_loop()
except KeyboardInterrupt:
    print("Exiting program.")
    ser.close()
    #froot.destroy()
