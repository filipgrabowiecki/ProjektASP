import math
import cv2
import numpy as np

values = [[150, 50], [152, 50], [152, 51], [152, 52], [151, 53], [150, 54], [149, 54],
        [151, 55], [210, -18], [210, -18], [215, -17], [210, -16], [215, -15]]

array1 = []
array2 = []

value0 = values[0]
array1_filled  = False

for i in range(len(values)):
        if i == 0:
                array1.append(values[0])
        else:
                if values[i][1] - values[i-1][1] <= 5 and values[i][1] - values[i-1][1] >= -5:
                        if not array1_filled:
                                array1.append(values[i])
                        else:
                                array2.append(values[i])
                else:
                        array2.append(values[i])
                        array1_filled = True


print(array1)
print(array2)

sumDistance_1 = 0
sumYaw_1 = 0
sumDistance_2 = 0
sumYaw_2 = 0
for element in array1:
        sumDistance_1 += element[0]
        sumYaw_1 += element[1]

for element in array2:
        sumDistance_2 += element[0]
        sumYaw_2 += element[1]

mean_dist_1 = int(round(sumDistance_1/len(array1), 0))
mean_yaw_1 = int(round(sumYaw_1/len(array1), 0))
mean_dist_2 = int(round(sumDistance_2/len(array2), 0))
mean_yaw_2 = int(round(sumYaw_2/len(array2), 0))

print(f"Mean dist Bottle 1: {mean_dist_1}\nMean yaw Bottle 1: {mean_yaw_1}")
print(f"Mean dist Bottle 2: {mean_dist_2}\nMean yaw Bottle 2: {mean_yaw_2}")
yaw_1 = 0
yaw_2 = 0

if mean_yaw_1 < 0:
      yaw_1 = 360 + mean_yaw_1
else:
        yaw_1 = mean_yaw_1

if mean_yaw_2 < 0:
      yaw_2 = 360 + mean_yaw_2
else:
        yaw_2 = mean_yaw_2

yaw_1_rad = math.radians(yaw_1)
x1 = int(round(mean_dist_1*math.sin(yaw_1_rad), 0))
y1 = int(round(mean_dist_1*math.cos(yaw_1_rad), 0))

yaw_2_rad = math.radians(yaw_2)
x2 = int(round(mean_dist_2*math.sin(yaw_2_rad), 0))
y2 = int(round(mean_dist_2*math.cos(yaw_2_rad), 0))

background = np.zeros((600, 600, 3), dtype=np.uint8)
cv2.circle(background, (300, 300), 5, (255, 0, 0), 2)
cv2.circle(background, (300+x1, 300-y1), 2, (0, 255, 0), 2)
cv2.circle(background, (300+x2, 300-y2), 2, (0, 255, 0), 2)
cv2.imshow("map", background)
cv2.waitKey(0)