import numpy as np
import os
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt


def load_and_extract_features(file_path):
    try:
        
        data = np.loadtxt(file_path, skiprows=1)  
        
        
        accel_x, accel_y, accel_z = data[:, 0], data[:, 1], data[:, 2]
        gyro_x, gyro_y, gyro_z = data[:, 3], data[:, 4], data[:, 5]
        
        
        features = [
            np.mean(accel_x), np.std(accel_x),
            np.mean(accel_y), np.std(accel_y),
            np.mean(accel_z), np.std(accel_z),
            np.mean(gyro_x), np.std(gyro_x),
            np.mean(gyro_y), np.std(gyro_y),
            np.mean(gyro_z), np.std(gyro_z)
        ]
        return features
    except Exception as e:
        print(f"Skipping file {file_path}: {e}")
        return None


def prepare_dataset(data_dir):
    X = []  
    y = []  
    
    
    gesture_folders = {'up_data': 0, 'down_data': 1, 'left_data': 2, 'right_data': 3}
    
   
    for folder_name, label in gesture_folders.items():
        folder_path = os.path.join(data_dir, folder_name)
        
        
        for file_name in os.listdir(folder_path):
            file_path = os.path.join(folder_path, file_name)
            if os.path.isfile(file_path):
                features = load_and_extract_features(file_path)
                if features is not None:  
                    X.append(features)
                    y.append(label)
    
    return np.array(X), np.array(y)


data_directory = "gesture_data"  
X, y = prepare_dataset(data_directory)


X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)


model = SVC(kernel='rbf')  
model.fit(X_train, y_train)


y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"Model Accuracy: {accuracy * 100:.2f}%")


print("Classification Report:")
print(classification_report(y_test, y_pred, target_names=['up', 'down', 'left', 'right']))


conf_matrix = confusion_matrix(y_test, y_pred)
sns.heatmap(conf_matrix, annot=True, cmap="Blues", fmt='g', 
            xticklabels=['up', 'down', 'left', 'right'], 
            yticklabels=['up', 'down', 'left', 'right'])
plt.title('Confusion Matrix')
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.show()
