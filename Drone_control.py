from djitellopy import tello
import time

# Initialize the Tello drone
print("test1")
drone = tello.Tello()
drone.connect()
print("test2")
# Take off once at the start
drone.takeoff()

try:
    while True:
        # Get the user input for direction
        command = input("Enter a command (l: left, r: right, u: up, d: down, q: quit): ").lower()

        # Movement commands using rc_control
        if command == 'l':
            drone.send_rc_control(-50, 0, 0, 0)  # Move left slightly
            time.sleep(0.5)  # Delay for command execution
        elif command == 'r':
            drone.send_rc_control(50, 0, 0, 0)   # Move right slightly
            time.sleep(0.5)  # Delay for command execution
        elif command == 'u':
            drone.send_rc_control(0, 0, 50, 0)   # Move up slightly
            time.sleep(0.5)  # Delay for command execution
        elif command == 'd':
            drone.send_rc_control(0, 0, -50, 0)  # Move down slightly
            time.sleep(0.5)  # Delay for command execution
        elif command == 'q':
            # Land the drone and break the loop
            drone.land()
            break
        else:
            print("Invalid command. Please enter 'l', 'r', 'u', 'd', or 'q'.")

        # Stop movement after each command
        drone.send_rc_control(0, 0, 0, 0)  # Stop movement
        time.sleep(0.2)  # Short delay to prevent command overlap

finally:
    # Ensure the drone connection is properly closed
    drone.end()
