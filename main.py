
from threading import Thread, Event
import time
from djitellopy import Tello
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

    def batteryTempCheck(self):
        self.bat_temp.update()

    def mapping_func(self):
        #ZMIANA
        if self.bottle_yaw is not None:
            return

        if len(self.list_of_bottles) > 0 and self.mapping_ended:
            self.bottle_yaw = self.mapping.update(self.list_of_bottles)

    def first_landing_func(self):
        if self.mission_rotate_done == True and self.mapping_ended == False:
            self.rc_control(0, 0, 0, 0)
            self.mapping_ended = True

    def follow_the_bottle(self):
        if self.bottle_yaw is not None and self.mission_fly == False:
            current_yaw = self.drone.get_yaw()
            print(self.list_of_bottles)
            print(f"Current_yaw: {current_yaw} BottleYaw: {self.bottle_yaw} ")
            if current_yaw + 15 > self.bottle_yaw > current_yaw - 15:
                self.rc_control(0,0,0,0)
                self.mission_fly = True
            else:
                self.rc_control(0, 0, 0, 25)


    def final_control(self):
        if self.final_mission_complete_rebel_is_gone == False:
            if self.mission_fly == True:
                order = self.object_detection.update(self.mission_rotate, self.mission_fly)
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
                        self.final_mission_complete_rebel_is_gone = True

    def objectDetection(self):
        bottle_position = self.object_detection.update(self.mission_rotate, self.mission_fly)
        if bottle_position is not None and self.mission_rotate_done == False:
            print("gotowe")
            self.list_of_bottles = bottle_position
            print(f"CZY TO TO?: {self.list_of_bottles}")
            self.mission_rotate_done = True

    def mission_func(self):
        if not self.mission_rotate_done:
            if self.yaw + 5 > self.drone.get_yaw() > self.yaw - 5:
                print("done")
                self.mission_rotate = False
            else:
                self.rc_control(0,0,0,25)

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

        follow_the_bottle_obj = self.Threading(0.1, self.stop_controller, self.follow_the_bottle)
        follow_the_bottle_obj.start()

        final_control_obj = self.Threading(0.1, self.stop_controller, self.final_control)
        final_control_obj.start()

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
        self.mission_rotate = True
        self.mission_rotate_done = False

        self.mapping_ended = False
        self.bottle_yaw = None
        self.list_of_bottles = []

        self.mission_fly = False
        self.final_mission_complete_rebel_is_gone = False


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
