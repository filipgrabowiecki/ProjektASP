import time
import math
import pygame

class Mapping:
    done = False
    points = None

    def update(self, points):
        if self.done:
            return

        self.filter(points)
        return self.display()


    def filter(self, points):
        remaped_points = []
        for i in points:
            new_yaw = 0
            if i[1] < 0:
                new_yaw = 360 + i[1]
                remaped_points.append([i[0], new_yaw])
            else:
                remaped_points.append([i[0], i[1]])

        a = 0
        yaw_sum = 0
        dist_sum = 0
        filtered = []

        for i in range(len(remaped_points)):
            a += 1
            if a == 1:
                yaw_sum += remaped_points[i][1]
                dist_sum += remaped_points[i][0]
            else:
                err = abs(remaped_points[i][1] - remaped_points[i-1][1])
                if 5 >= err:
                    yaw_sum += remaped_points[i][1]
                    dist_sum += remaped_points[i][0]
                    if i == len(remaped_points) - 1:
                        filtered.append([int(round(dist_sum / a, 0)), int(round(yaw_sum / a, 0))])
                else:
                    filtered.append([int(round(dist_sum / (a - 1), 0)), int(round(yaw_sum / (a - 1), 0))])
                    dist_sum = 0
                    yaw_sum = 0
                    a = 0

        self.points = filtered
        print(self.points)

    def display(self):
        pygame.init()
        width, height = 600, 600
        window = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Map")
        black = (0, 0, 0)
        active_index = None

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if pygame.K_1 <= event.key <= pygame.K_9:
                        index = event.key - pygame.K_1
                        if index < len(self.points):
                            active_index = index
                            running = False

            window.fill(black)

            for index, i in enumerate(self.points):
                radians = math.radians(i[1])
                x = int(round(i[0] * math.sin(radians), 0))
                y = int(round(i[0] * math.cos(radians), 0))
                print(f"x: {x}, y: {y}")

                pygame.draw.circle(window, (0, 255, 0), (300 + x, 300 - y), 5, 1)
                if index == active_index:
                    pygame.draw.circle(window, (255, 0, 0), (x, y), 6, 1)  # Obwódka dla aktywnego okręgu

            pygame.draw.circle(window, (0, 0, 255), (300, 300), 5, 1)  # Obwódka dla aktywnego okręgu
            pygame.display.flip()

        pygame.quit()
        self.done = True
        print(f"active_index: {active_index}")
        return self.points[active_index]


