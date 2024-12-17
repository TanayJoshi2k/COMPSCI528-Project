import serial
import pandas as pd
import joblib
import re
import numpy as np
import time
from djitellopy import tello

# Column names for the dataframe
column_names = ['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z']

# Serial port configuration
serial_port = 'COM4'
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate, timeout=0.01)

# Load the trained model
loaded_model = joblib.load('Trained_model/xgboost_model_v2.pkl')

# Labels for predictions
labels = ["UP", "DOWN", "LEFT", "RIGHT", "REST", "FORWARD", "BACKWARD", "NEW_CLOCKWISE"]

# Sliding window parameters
window_size = 400
df = pd.DataFrame(columns=column_names)

# Initialize the Tello drone
drone = tello.Tello()
drone.connect()
battery_percentage = drone.get_battery()
print(f"Drone Battery Percentage: {battery_percentage}%")
drone.takeoff()

# Mapping gestures to drone commands
gesture_to_command = {
    "UP": (0, 0, 50, 0),        # Move up
    "DOWN": (0, 0, -50, 0),     # Move down
    "LEFT": (-50, 0, 0, 0),     # Move left
    "RIGHT": (50, 0, 0, 0),     # Move right
    "FORWARD": (0, 50, 0, 0),   # Move forward
    "BACKWARD": (0, -50, 0, 0), # Move backward
    "NEW_CLOCKWISE": (0, 0, 0, 180), # Rotate clockwise
    "REST": (0, 0, 0, 0)        # Hover
}

def read_sensor_data(ser):
    try:
        data = ser.readline().decode('utf-8').strip()
        row = data.split(",")
        if len(row) >= 7:
            cleaned_row = [re.sub(r'[^\d.-]', '', value) for value in row[1:7]]
            return list(map(float, cleaned_row))
    except Exception as e:
        print(f"Error processing sensor data: {e}")
    return None

def preprocess_data_for_inference(df, fixed_length=400):
    if not df.empty:
        df['acce_magnitude'] = np.sqrt(df['acce_x']**2 + df['acce_y']**2 + df['acce_z']**2)
        df['gyro_magnitude'] = np.sqrt(df['gyro_x']**2 + df['gyro_y']**2 + df['gyro_z']**2) 

        data = df[['gyro_x', 'gyro_y', 'gyro_z', 'acce_x', 'acce_y', 'acce_z', "acce_magnitude", "gyro_magnitude"]].values.astype(np.float32)
        data = (data - data.mean(axis=0))

        if len(data) > fixed_length:
            data = data[:fixed_length]
        elif len(data) < fixed_length:
            padding = np.zeros((fixed_length - len(data), data.shape[1]), dtype=np.float32)
            data = np.vstack((data, padding))

        return data.flatten().reshape(1, -1)
    else:
        raise ValueError("DataFrame is empty. Cannot preprocess for inference.")

def predict_gesture(data_frame, confidence_threshold=0.00):
    try:
        features = preprocess_data_for_inference(data_frame)
        probabilities = loaded_model.predict_proba(features)[0]
        max_prob = max(probabilities)
        predicted_class = probabilities.argmax()

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
    global df
    collecting = True
    types = 0
    try:
        while True:
            if collecting:
                sensor_data = read_sensor_data(ser)
                if sensor_data:
                    df.loc[len(df)] = sensor_data
                    print(len(df))
                    if len(df) == window_size:
                        collecting = False
                        try:
                            prediction, confidence = predict_gesture(df)
                            print(f"Predicted Gesture: {prediction} with Confidence: {confidence*100:.1f}%")
                            # df.to_csv(f"Testing/{types}_{prediction}.csv")
                            types += 1

                            # Execute drone command
                            if prediction in gesture_to_command:
                                command = gesture_to_command[prediction]
                                drone.send_rc_control(*command)
                                time.sleep(0.5)
                                drone.send_rc_control(0, 0, 0, 0)  # Stop movement
                        except Exception as e:
                            print(f"Prediction error: {e}")
            else:
                collecting = True
                time.sleep(2)
                ser.reset_input_buffer()
                df = pd.DataFrame(columns=column_names)
    except KeyboardInterrupt:
        print("Exiting program.")
        drone.land()
        drone.end()
        ser.close()

# Run the main loop
main_loop()