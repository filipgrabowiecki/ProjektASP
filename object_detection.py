import cv2
from ultralytics import YOLO

class ObjectDetection:

    def __init__(self, tello_drone):
        self.drone = tello_drone
        self.model = YOLO('yolov8n.pt')
        self.list_of_bottle_position = []
        self.first_order = None

    def update(self, mission_rotate, mission_fly):
        img = self.drone.get_frame_read().frame
        results = self.model(img, verbose=False)

        list_of_objects = [results[0].boxes.cls]

        values_list_float = list_of_objects[0].tolist()

        object_values_list = []
        for i in values_list_float:
            object_values_list.append(int(i))

        #DO SPRAWDZENIA
        # list_of_xyxy_float = results[0].boxes.xyxy.tolist()

        xyxy = [results[0].boxes.xyxy]

        list_of_xyxy_float = xyxy[0].tolist()
        list_of_xyxy = []

        for i in list_of_xyxy_float:
            new_list = []
            for j in i:
                new_list.append(int(j))
            list_of_xyxy.append(new_list)


        #DO SPRAWDZENIA
        # list_of_xyxy = [int(i) for i in list_of_xyxy_float]

        bottle_index = -1

        for i in object_values_list:
            if i == 39:
                bottle_index = object_values_list.index(i)

        if bottle_index != -1:
            bottle_xyxy = list_of_xyxy[bottle_index]
            left = bottle_xyxy[0]
            top = bottle_xyxy[1]
            width = bottle_xyxy[2] - bottle_xyxy[0]
            height = bottle_xyxy[3] - bottle_xyxy[1]
            width_dif = (960 - width)/2
            height_dif = (720 - height)/2

            if not mission_fly:
                if mission_rotate:
                    if left > width_dif - 20 and left < (width_dif + 20 + width):
                        distance_from_obj = int(round(36420*height**(-1.059), 0))
                        bottle_yaw = self.drone.get_yaw()
                        self.list_of_bottle_position.append([distance_from_obj, bottle_yaw])
                        print("Dodaje")
                        return None
                else:
                    return self.list_of_bottle_position
            else:

                if left > (width_dif + 50 + width):
                    # print("DRONE RIGHT")
                    self.first_order = "right"

                elif left < width_dif - 50:
                    self.first_order = "left"

                elif left > width_dif - 50 and left < (width_dif + 50 + width):

                    if top > (height_dif + 100 + height):
                        self.first_order = "down"

                    if top < height_dif - 100:

                        self.first_order = "up"

                    if top > (height_dif - 100) and top < (height_dif + 100 + height):

                        self.first_order = "straight"

                        if height > 300:
                            self.first_order = "land"

                image_ready = results[0].plot()
                cv2.imshow('image', image_ready)
                cv2.waitKey(1)
                return self.first_order

        image_ready = results[0].plot()
        cv2.imshow('image', image_ready)
        cv2.waitKey(1)