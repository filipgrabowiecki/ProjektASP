import math
import cv2
import numpy as np

old_all_points = [[126, 59], [120, 61], [121, 63], [120, 63], [121, 64], [121, 66], [181, -85], [178, -84], [181, -84], [177, -82], [179, -80]]
all_points = []
for i in old_all_points:
    new_yaw = 0
    if i[1] < 0:
        new_yaw = 360 + i[1]
        all_points.append([i[0], new_yaw])
    else:
        all_points.append([i[0], i[1]])

a = 0
yaw_sum = 0
dist_sum = 0
new_points = []

for i in range(len(all_points)):
    a += 1
    if a == 1:
        yaw_sum += all_points[i][1]
        dist_sum += all_points[i][0]
    else:
        if 5 >= all_points[i][1] - all_points[i - 1][1] >= -5:
            yaw_sum += all_points[i][1]
            dist_sum += all_points[i][0]
            if i == len(all_points) - 1:
                new_points.append([int(round(dist_sum/a, 0)), int(round(yaw_sum/a, 0))])
        else:
            new_points.append([int(round(dist_sum/(a-1), 0)), int(round(yaw_sum/(a-1), 0))])
            dist_sum = 0
            yaw_sum = 0
            a = 0
print(new_points)

background = np.zeros((600, 600, 3), dtype=np.uint8)
cv2.circle(background, (300, 300), 5, (255, 0, 0), 2)
for i in new_points:
    radians = math.radians(i[1])
    x = int(round(i[0]*math.sin(radians), 0))
    y = int(round(i[0]*math.cos(radians), 0))
    cv2.circle(background, (300 + x, 300 - y), 3, (0, 255, 0), 2)

cv2.imshow("mapping", background)
cv2.waitKey(0)
cv2.destroyAllWindows()


