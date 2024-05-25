import cv2
from ultralytics import YOLO

class ObjectDetection:

    def __init__(self, tello_drone):
        self.drone = tello_drone
        self.model = YOLO('yolov8n.pt')
        self.list_of_bottle_position = []
        self.is_it_done = False

    def update(self, mission):
        mission1 = mission
        img = self.drone.get_frame_read().frame
        results = self.model(img, verbose=False, conf=0.5)

        list_of_objects = [results[0].boxes.cls]

        values_list_float = list_of_objects[0].tolist()

        object_values_list = []
        for i in values_list_float:
            object_values_list.append(int(i))

        xyxy = [results[0].boxes.xyxy]

        list_of_xyxy_float = xyxy[0].tolist()
        list_of_xyxy = []

        for i in list_of_xyxy_float:
            new_list = []
            for j in i:
                new_list.append(int(j))
            list_of_xyxy.append(new_list)

        person_indx = -1

        for i in object_values_list:
            if i == 39:
                person_indx = object_values_list.index(i)

        if person_indx != -1:
            person_xyxy = list_of_xyxy[person_indx]
            # print(person_xyxy)
            left = person_xyxy[0]
            top = person_xyxy[1]
            width = person_xyxy[2] - person_xyxy[0]
            height = person_xyxy[3] - person_xyxy[1]
            width_dif = (960- width)/2
            if not self.is_it_done:
                if mission1:
                    print("mission - True")
                    if left > width_dif - 20 and left < (width_dif + 20 + width):
                        distance_from_obj = int(round(36420*height**(-1.059), 0))
                        bottle_yaw = self.drone.get_yaw()
                        print("DODAJE")
                        self.list_of_bottle_position.append([distance_from_obj, bottle_yaw])
                        return None
                else:
                    print("mission - FALSE")
                    return self.list_of_bottle_position
                    self.is_it_done = True

            # print(f"top: {top} left: {left} width: {width} height: {height}")

        image_ready = results[0].plot()
        cv2.imshow('image', image_ready)
        cv2.waitKey(1)