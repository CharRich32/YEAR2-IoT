from rplidar import RPLidar
import numpy as np                                          
import matplotlib.pyplot as plt
import cv2
from datetime import datetime
import ScanType as ScanType
import time
import LED as LED
import matplotlib.animation as animation
import logging
import os
#from azure.iot.device import IoTHubDeviceClient, Message

# Configure logger for RPLidar
logger = logging.getLogger('rplidar')
logger.setLevel(logging.DEBUG)

# Create a handler and set the log level
handler = logging.StreamHandler()
handler.setLevel(logging.WARNING)

# Create a formatter and add it to the handler
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(handler)

# Initialize the USB camera
cap = cv2.VideoCapture(0)

# Initiating LED Variables
GREEN_LED = 18
RED_LED = 23

# Distance to check
MAX_DISTANCE = 200

# Azure IoT Hub connection string
CONNECTION_STRING = "HostName=IoTTrafficLightPy.azure-devices.net;DeviceId=mypi;SharedAccessKey=xNpsZSYscJtPnody4WrJcHQZnu/6kt/he1uQvjnYJwY="

# Create an instance of IoT Hub Device Client
iot_hub_client = None

data = []

def initialize_lidar():
    global lidar
    # Create RPLidar instance
    lidar = RPLidar('/dev/ttyUSB0', baudrate=256000)

def initialize_iot_client():
    global iot_hub_client
    # Create an instance of IoT Hub Device Client
    #iot_hub_client = IoTHubDeviceClient.create_from_connection_string(CONNECTION_STRING)

def initialize_camera():
    # Open the USB camera
    cap.open(0)

def cleanup():
    # Release the USB camera
    cap.release()

    # Disconnect the IoT Hub client
    if iot_hub_client:
        iot_hub_client.disconnect()

    # Stop and disconnect the lidar
    lidar.stop_motor()
    lidar.stop()
    lidar.disconnect()

def save_image(dt, distance):
    ret, frame = cap.read()
    # Save the captured frame as an image file
    cv2.imwrite('/home/pi/Documents/LidarProject/images/image' + str(dt) + '.jpg', frame)

# 3D pointcloud generation - no longer used
def get_pointcloud(distances, angles):
    # Convert distances and angles to 3D Cartesian coordinates
    x = np.multiply(distances, np.cos(angles))
    y = np.multiply(distances, np.sin(angles))
    z = np.zeros(len(distances))

    point_cloud = np.vstack((x, y, z)).transpose()

    return point_cloud

def process_scan(i, scan):
    (quality, angle, distance) = scan
    dt = datetime.now()
    scan_class = ScanType.ScanType(i, dt, quality, angle, distance)
    #message = Message('Scan details: quality={}, angle={}, distance={}'.format(quality, angle, distance))
    #iot_hub_client.send_message(message)
    if distance < MAX_DISTANCE:
        LED.turn_on(RED_LED)
        LED.turn_off(GREEN_LED)
        #save_image(dt, distance)
        data.append(scan_class)
        print(scan_class)
    else:
        LED.turn_on(GREEN_LED)
        LED.turn_off(RED_LED)


def run_lidar_scan():
    # Start scanning
    lidar.start_motor()

    # Clean input buffer
    lidar.clean_input()

    try:
        for i, scans in enumerate(lidar.iter_scans(max_buf_meas=5000)):
            distances = []
            for scan in scans:
                (quality, angle, distance) = scan
                process_scan(i, scan)
                distances.append(distance)
            if i >= 6000:
                break
    except KeyboardInterrupt:
        print("Stopping")
    except Exception as e:
        print(e)
    finally:
        cleanup()

def plot_pointcloud():
    distances = []
    angles = []

    for scan in data:
        distances.append(scan.distance)
        angles.append(scan.angle)

    # Convert to radians
    angles = np.radians(angles)

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='polar')

    ax.scatter(angles, distances, s=1)

    ax.set_rmax(MAX_DISTANCE)
    ax.set_title('360-Degree 2D Scatter Plot')

    plt.show()

# Main execution
if __name__ == "__main__":
    try:
        initialize_lidar()
        initialize_iot_client()
        initialize_camera()

        # Start the lidar scan
        run_lidar_scan()

        # Plot the point cloud
        plot_pointcloud()
    except Exception as e:
        print(e)
