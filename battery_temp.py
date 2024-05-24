
class Battery_temp:

    def __init__(self, tello_drone):
        self.drone = tello_drone

    def update(self):
        print(f"\nBATTERY: {self.drone.get_battery()}")
        print(f"TEMPERATURE: {self.drone.get_temperature()}\n")
