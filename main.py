
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
import mapping


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

    def mapping_func(self):
        if len(self.new_list_of_bottle_position) > 0:
            self.mapping.update(self.new_list_of_bottle_position)
    def batteryTempCheck(self):
        self.bat_temp.update()

    def first_landing_func(self):
        if self.mission1_done == True and self.mapping_ended == False:
            self.rc_control(0, 0, 0, 0)
            self.mission1_done = False
            
            
            #self.drone.land()
            self.mapping_ended = True

    def bottle_input(self):
        if self.mapping_ended and self.provide_bottle_index == False:
            bottle_index = int(input("Podaj indeks butelki: "))
            self.newest_yaw = self.new_list_of_bottle_position[bottle_index][1]
            self.provide_bottle_index = True
            self.mission15 = True


    def stop_by_the_bottle(self): #follow_the_bottle
        if self.mission15 == True and self.mission_follow == False:
            if self.yaw + 5 > self.newest_yaw > self.yaw - 5:
                self.rc_control(0,0,0,0)
                self.mission_follow = True
            else:
                self.rc_control(0, 0, 0, 15)


    def follow_the_bottle(self): #final_control
        if self.mission_end == False: #final mission imperium cos tam kurwa
            if self.mission_follow == True:
                order = self.object_detection.update(self.mission_bottle_addition, self.mission_follow)
                if order is not None:
                    if order == "right":
                        self.rc_control(0,0,0, 10)
                    elif order == "left":
                        self.rc_control(0, 0, 0, -10)
                    elif order == "up":
                        self.rc_control(0, 0, 10, 0)
                    elif order == "down":
                        self.rc_control(0, 0, -10, 0)
                    elif order == "straight":
                        self.rc_control(0, 20, 0, 0)
                    elif order == "land":
                        self.rc_control(0,0,0,0)
                        time.sleep(2)
                        self.drone.land()
                        self.mission_end = True #final mission imperium cos tam kurwa
    def objectDetection(self):
        self.list_of_bottle_position = self.object_detection.update(self.mission_bottle_addition, self.mission_follow)
        if self.list_of_bottle_position is not None and self.mission1_done == False:
            print("gotowe")
            self.new_list_of_bottle_position = self.list_of_bottle_position
            print(f"CZY TO TO?: {self.new_list_of_bottle_position}")
            self.mission1_done = True

    def mission_func(self):
        print(f"start_yaw: {self.yaw} yaw:{self.drone.get_yaw()}")
        if not self.mission1_done:
            if self.yaw + 5 > self.drone.get_yaw() > self.yaw - 5:
            # if self.drone.get_yaw() > 100:
                print("done")
                self.mission_bottle_addition = False
                # print(self.mission1)
            else:
                # print(self.mission1)
                self.rc_control(0,0,0,15)
    def main(self):
        self.kill_switch = self.TelloKillSwitch(self)
        self.kill_switch.start()
        self.stop_controller = Event()

        battery_temp_obj = self.Threading(20.0, self.stop_controller, self.batteryTempCheck)
        battery_temp_obj.start()

        object_detection_obj = self.Threading(0.001, self.stop_controller, self.objectDetection)
        object_detection_obj.start()

        first_landing_func_obj = self.Threading(0.001, self.stop_controller, self.first_landing_func)
        first_landing_func_obj.start()

        mapping_func_obj = self.Threading(0.1, self.stop_controller, self.mapping_func)
        mapping_func_obj.start()

        time.sleep(5)
        self.drone.takeoff()
        time.sleep(5)
        self.yaw = self.drone.get_yaw()
        self.rc_control(0, 0, 0, 15)
        time.sleep(3)

        mission_func_obj = self.Threading(0.2, self.stop_controller, self.mission_func)
        mission_func_obj.start()



    def __init__(self):
        self.yaw = 0
        self.mission_bottle_addition = True #mision1
        self.mission_follow = False #mission2
        self.mission1_done = False
        self.mapping_ended = False
        self.new_list_of_bottle_position = []
        self.mission_end = False #final mission imperium cos tam kurwa

        self.drone = Tello()
        self.drone.connect()
        self.drone.streamon()

        self.bat_temp = battery_temp.Battery_temp(self.drone)
        self.object_detection = object_detection.ObjectDetection(self.drone)
        self.mapping = mapping.Mapping()

        self.main()
        time.sleep(300)
        self.drone.land()
        self.drone.end()


if __name__ == "__main__":
    td = TelloDrone()
