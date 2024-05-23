from threading import Thread, Event
from ultralytics import YOLO
import time
from djitellopy import Tello
import csv
import matplotlib.pyplot as plt
import cv2
import numpy as np
import keyboard


import battery_temp
import object_detection


class TelloDrone:

    class TelloKillSwitch(Thread):

        tc_handler = None

        def __init__(self, tc_handler):
            Thread.__init__(self)
            self.tc_handler = tc_handler

        def run(self):
            keyboard.wait('space')
            self.tc_handler.force_emergency_stop()


    class Threading(Thread):
        interval = 1.0
        running = None
        func = None

        def __init__(self, interval, event, func):
            Thread.__init__(self)
            self.running = event
            self.interval = interval
            self.func = func

        def run(self):
            while not self.running.wait(self.interval):
                self.func()

    drone = None
    stop_controller = None

    def force_emergency_stop(self):
        self.drone.emergency()
        self.stop_controller.set()

    def rc_control(self, lr, fb, up, y):
        self.drone.send_rc_control(left_right_velocity=lr, forward_backward_velocity=fb,
                                   up_down_velocity=up, yaw_velocity=y)


    def batteryTempCheck(self):
        self.bat_temp.update()

    def objectDetection(self):
        self.list_of_bottle_position = self.object_detection.update(self.mission1)
        print(self.list_of_bottle_position)

    def main(self):
        self.kill_switch = self.TelloKillSwitch(self)
        self.kill_switch.start()
        self.stop_controller = Event()

        battery_temp_obj = self.Threading(1.0, self.stop_controller, self.batteryTempCheck)
        battery_temp_obj.start()

        object_detection_obj = self.Threading(0.001, self.stop_controller, self.objectDetection)
        object_detection_obj.start()


    def __init__(self):
        self.mission1 = True

        self.drone = Tello()
        self.drone.connect()
        self.drone.streamon()

        self.bat_temp = battery_temp.Battery_temp(self.drone)
        self.object_detection = object_detection.ObjectDetection(self.drone)

        self.main()

        time.sleep(10)
        self.drone.takeoff()
        time.sleep(5)
        yaw = self.drone.get_yaw()
        self.rc_control(0, 0, 0, 15)
        time.sleep(1)
        while True:
            if self.drone.get_yaw() == yaw:
                break
            else:
                continue
        time.sleep(3)
        self.drone.land()
        time.sleep(20)


if __name__ == "__main__":
    td = TelloDrone()